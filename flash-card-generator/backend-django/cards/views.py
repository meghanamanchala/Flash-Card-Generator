import re

from django.contrib.auth import logout
from django.db.models import Count
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuthToken, FlashCard, LearningUnit
from .serializers import (
    FlashCardSerializer,
    LearningUnitSerializer,
    LoginSerializer,
    RegisterSerializer,
    ReviewFlashCardsSerializer,
    UserSerializer,
)

NUMBER_WORDS = {
    0: 'zero',
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine',
    10: 'ten',
    11: 'eleven',
    12: 'twelve',
}


def split_into_flashcard_chunks(raw_content, max_words=80):
    normalized_content = re.sub(r'\r\n?', '\n', raw_content).strip()
    if not normalized_content:
        return []

    paragraph_candidates = [
        block.strip()
        for block in re.split(r'\n\s*\n+', normalized_content)
        if block.strip()
    ]

    chunks = []
    for paragraph in paragraph_candidates:
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        sentence_candidates = [sentence.strip() for sentence in sentences if sentence.strip()]

        if len(sentence_candidates) > 1:
            pending_sentence = None

            def flush_sentence(value):
                if not value:
                    return

                sentence_words = value.split()
                sentence_length = len(sentence_words)

                if sentence_length > max_words:
                    for start in range(0, sentence_length, max_words):
                        piece = ' '.join(sentence_words[start:start + max_words]).strip()
                        if len(piece.split()) >= 5:
                            chunks.append(piece)
                    return

                if sentence_length >= 5:
                    chunks.append(value)

            for sentence in sentence_candidates:
                if sentence.endswith('?'):
                    if pending_sentence:
                        flush_sentence(f'{pending_sentence} {sentence}')
                        pending_sentence = None
                    else:
                        flush_sentence(sentence)
                    continue

                if pending_sentence:
                    flush_sentence(pending_sentence)

                pending_sentence = sentence

            if pending_sentence:
                flush_sentence(pending_sentence)

            continue

        words = paragraph.split()
        if len(words) <= max_words:
            if len(words) >= 5:
                chunks.append(paragraph)
            continue

        current_chunk = []
        current_length = 0
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_words = sentence.split()
            sentence_length = len(sentence_words)

            if sentence_length > max_words:
                if current_chunk:
                    chunks.append(' '.join(current_chunk).strip())
                    current_chunk = []
                    current_length = 0

                for start in range(0, sentence_length, max_words):
                    piece = ' '.join(sentence_words[start:start + max_words]).strip()
                    if len(piece.split()) >= 5:
                        chunks.append(piece)
                continue

            if current_length + sentence_length > max_words and current_chunk:
                chunks.append(' '.join(current_chunk).strip())
                current_chunk = [sentence]
                current_length = sentence_length
            else:
                current_chunk.append(sentence)
                current_length += sentence_length

        if current_chunk:
            chunks.append(' '.join(current_chunk).strip())

    return [chunk for chunk in chunks if len(chunk.split()) >= 5]


def normalize_flashcard_statement(value):
    value = re.sub(r'\s+', ' ', value).strip()
    value = re.sub(r'^(?:[-*•]\s+|\d+[.)]\s+)', '', value)
    return value.strip(' .')


def finalize_sentence(value):
    value = value.strip()
    if not value:
        return ''
    if value[-1] not in '.!?':
        value = f'{value}.'
    return value


def starts_with_auxiliary(value):
    return bool(
        re.match(
            r'^(is|are|was|were|can|could|should|would|do|does|did|has|have|had)\b',
            value.strip(),
            re.IGNORECASE,
        )
    )


def normalize_answer(value):
    value = value.strip()
    if not value:
        return ''
    return value if starts_with_auxiliary(value) else finalize_sentence(value)


def strip_discourse_prefix(value):
    return re.sub(
        r'^(?:now|next|then|finally|remember|imagine|suppose|consider|note|overall|first|second|third)\b[:,]?\s*',
        '',
        value.strip(),
        flags=re.IGNORECASE,
    )


def clean_subject(value):
    cleaned_value = strip_discourse_prefix(value).strip(' ,.:;')
    return re.sub(r'^(The|A|An)\b', lambda match: match.group(1).lower(), cleaned_value)


def clean_question_text(value):
    value = strip_discourse_prefix(value).strip()
    value = re.sub(r'\s+', ' ', value)
    value = value.rstrip('?.! ')

    if not value:
        return 'What should you remember from this note?'

    return f'{value[0].upper()}{value[1:]}?'


def subject_is_plural(subject):
    normalized_subject = re.sub(r'^(the|a|an)\s+', '', clean_subject(subject), flags=re.IGNORECASE).lower()

    if not normalized_subject:
        return False

    if ' and ' in normalized_subject:
        return True

    singular_exceptions = ('ss', 'us', 'ics')
    if normalized_subject.endswith(singular_exceptions):
        return False

    return normalized_subject.endswith('s')


def do_auxiliary(subject):
    return 'do' if subject_is_plural(subject) else 'does'


def split_list_items(value):
    normalized_value = re.sub(r'\s+', ' ', value).strip(' .')
    if not normalized_value:
        return []

    parts = [
        re.sub(r'^(?:and|or)\s+', '', part.strip(' .'), flags=re.IGNORECASE)
        for part in re.split(r';\s*|,(?![^()]*\))\s*|\s+(?:and|or)\s+', normalized_value)
        if re.sub(r'^(?:and|or)\s+', '', part.strip(' .'), flags=re.IGNORECASE)
    ]
    return parts


def format_list_answer(items):
    cleaned_items = [item.strip(' .') for item in items if item.strip(' .')]
    if not cleaned_items:
        return ''

    if len(cleaned_items) == 1:
        return finalize_sentence(cleaned_items[0])

    if len(cleaned_items) == 2:
        return finalize_sentence(f'{cleaned_items[0]} and {cleaned_items[1]}')

    return '\n'.join(f'{index}. {item}' for index, item in enumerate(cleaned_items, start=1))


def normalize_count_phrase(raw_count, fallback_count):
    normalized_value = (raw_count or '').strip().lower()
    if not normalized_value:
        return NUMBER_WORDS.get(fallback_count, str(fallback_count))

    if normalized_value.isdigit():
        numeric_value = int(normalized_value)
        return NUMBER_WORDS.get(numeric_value, str(numeric_value))

    return normalized_value


def build_components_question(subject, raw_count, items, label='components'):
    item_count = len(items)
    count_phrase = normalize_count_phrase(raw_count, item_count)

    if item_count >= 2:
        return f'What are the {count_phrase} {label} of {subject}?'

    return f'What does {subject} include?'


def build_question_answer_pair(chunk):
    statement = normalize_flashcard_statement(chunk)

    if not statement:
        return None

    sentence_candidates = [
        normalize_flashcard_statement(sentence)
        for sentence in re.split(r'(?<=[.!?])\s+', statement)
        if normalize_flashcard_statement(sentence)
    ]
    question_sentences = [sentence for sentence in sentence_candidates if sentence.endswith('?')]
    factual_sentences = [sentence for sentence in sentence_candidates if not sentence.endswith('?')]

    if question_sentences and factual_sentences:
        return {
            'question': clean_question_text(question_sentences[-1]),
            'answer': ' '.join(finalize_sentence(sentence) for sentence in factual_sentences),
            'content': finalize_sentence(statement),
        }

    naming_match = re.match(
        r'^(?P<subject>.+?)\s+(?P<be>is|are)\s+'
        r'(?P<label>called|known as|referred to as)\s+'
        r'(?P<name>.+?)(?:\s+because\s+(?P<reason>.+))?$',
        statement,
        re.IGNORECASE,
    )
    if naming_match:
        subject = clean_subject(naming_match.group('subject'))
        be_verb = naming_match.group('be').lower()
        label = naming_match.group('label').lower()
        name = naming_match.group('name').strip()
        reason = naming_match.group('reason')

        if reason:
            return {
                'question': f"Why {be_verb} {subject} {label} {name}?",
                'answer': normalize_answer(f"Because {reason.strip()}"),
                'content': finalize_sentence(statement),
            }

        return {
            'question': f"What {be_verb} {subject} {label}?",
            'answer': finalize_sentence(name),
            'content': finalize_sentence(statement),
        }

    function_match = re.match(
        r'^(?:the\s+)?function of (?P<subject>.+?) is to (?P<predicate>.+)$',
        statement,
        re.IGNORECASE,
    )
    if function_match:
        subject = clean_subject(function_match.group('subject'))
        predicate = function_match.group('predicate').strip()
        return {
            'question': f'What is the function of {subject}?',
            'answer': normalize_answer(f'It is to {predicate}'),
            'content': finalize_sentence(statement),
        }

    stands_for_match = re.match(
        r'^(?P<subject>.+?) stands for (?P<predicate>.+)$',
        statement,
        re.IGNORECASE,
    )
    if stands_for_match:
        subject = clean_subject(stands_for_match.group('subject'))
        predicate = stands_for_match.group('predicate').strip()
        return {
            'question': f'What does {subject} stand for?',
            'answer': finalize_sentence(predicate),
            'content': finalize_sentence(statement),
        }

    structure_match = re.match(
        r'^(?:the\s+)?structure of (?P<subject>.+?) includes (?P<items>.+)$',
        statement,
        re.IGNORECASE,
    )
    if structure_match:
        subject = clean_subject(structure_match.group('subject'))
        items = split_list_items(structure_match.group('items'))
        answer = format_list_answer(items)
        if answer:
            return {
                'question': build_components_question(subject, '', items, 'structural components'),
                'answer': answer,
                'content': finalize_sentence(statement),
            }

    stages_match = re.match(
        r'^(?P<subject>.+?) occurs in (?P<count>[\w-]+) main stages?: (?P<items>.+)$',
        statement,
        re.IGNORECASE,
    )
    if stages_match:
        subject = clean_subject(stages_match.group('subject'))
        items = split_list_items(stages_match.group('items'))
        answer = format_list_answer(items)
        if answer:
            count_phrase = normalize_count_phrase(stages_match.group('count'), len(items))
            return {
                'question': f'What are the {count_phrase} main stages of {subject}?',
                'answer': answer,
                'content': finalize_sentence(statement),
            }

    composition_match = re.match(
        r'^(?P<subject>.+?)\s+(?:consists of|include[s]?|contains|is composed of)\s+(?P<items>.+)$',
        statement,
        re.IGNORECASE,
    )
    if composition_match:
        subject = clean_subject(composition_match.group('subject'))
        items = split_list_items(composition_match.group('items'))
        answer = format_list_answer(items)
        if answer:
            return {
                'question': build_components_question(subject, '', items),
                'answer': answer,
                'content': finalize_sentence(statement),
            }

    responsibility_match = re.match(
        r'^(?P<subject>.+?) is responsible for (?P<predicate>.+)$',
        statement,
        re.IGNORECASE,
    )
    if responsibility_match:
        subject = clean_subject(responsibility_match.group('subject'))
        predicate = responsibility_match.group('predicate').strip()
        return {
            'question': f'What is {subject} responsible for?',
            'answer': finalize_sentence(predicate),
            'content': finalize_sentence(statement),
        }

    location_match = re.match(
        r'^(?P<subject>.+?)\s+(?:occurs?|happens?|is found|is located)\s+in\s+(?P<location>.+)$',
        statement,
        re.IGNORECASE,
    )
    if location_match:
        subject = clean_subject(location_match.group('subject'))
        location = location_match.group('location').strip()
        return {
            'question': f'Where does {subject} occur?',
            'answer': finalize_sentence(location),
            'content': finalize_sentence(statement),
        }

    patterns = [
        (
            re.compile(r'^(?P<subject>.+?)\s+(?P<verb>is|are)\s+(?P<predicate>.+)$', re.IGNORECASE),
            lambda match: {
                'question': (
                    f"Why {match.group('verb').lower()} {clean_subject(match.group('subject'))} {match.group('predicate').split(' because ', 1)[0].strip()}?"
                    if ' because ' in match.group('predicate').lower()
                    else f"What {match.group('verb').lower()} {clean_subject(match.group('subject'))}?"
                ),
                'answer': (
                    normalize_answer(f"Because {match.group('predicate').split(' because ', 1)[1].strip()}")
                    if ' because ' in match.group('predicate').lower()
                    else finalize_sentence(match.group('predicate'))
                ),
            },
        ),
        (
            re.compile(
                r'^(?P<subject>.+?)\s+'
                r'(?P<verb>helps?|allow[s]?|enable[s]?|support[s]?|provide[s]?|store[s]?|contain[s]?|produce[s]?|transport[s]?|regulate[s]?|control[s]?|protect[s]?|maintain[s]?|convert[s]?|trigger[s]?|release[s]?|form[s]?|include[s]?|cause[s]?)\s+'
                r'(?P<predicate>.+)$',
                re.IGNORECASE,
            ),
            lambda match: {
                'question': f"What {do_auxiliary(clean_subject(match.group('subject')))} {clean_subject(match.group('subject'))} do?",
                'answer': finalize_sentence(
                    f"{clean_subject(match.group('subject'))} {match.group('verb').strip()} {match.group('predicate').strip()}"
                ),
            },
        ),
        (
            re.compile(r'^(?P<subject>.+?):\s*(?P<predicate>.+)$', re.IGNORECASE),
            lambda match: {
                'question': f"What should you know about {clean_subject(match.group('subject'))}?",
                'answer': finalize_sentence(match.group('predicate')),
            },
        ),
    ]

    for pattern, builder in patterns:
        match = pattern.match(statement)
        if not match:
            continue

        pair = builder(match)
        question = pair['question'].strip()
        answer = pair['answer'].strip()

        if question and answer:
            return {
                'question': clean_question_text(question),
                'answer': answer,
                'content': finalize_sentence(statement),
            }

    words = statement.split()
    subject = clean_subject(' '.join(words[: min(6, len(words))]))

    return {
        'question': f'What should you remember about {subject}?' if subject else 'What should you remember from this note?',
        'answer': finalize_sentence(statement),
        'content': finalize_sentence(statement),
    }


def merge_chunks_to_limit(chunks, limit):
    if limit <= 0:
        return []

    if len(chunks) <= limit:
        return chunks

    group_size = -(-len(chunks) // limit)
    merged_chunks = [
        ' '.join(chunks[index:index + group_size]).strip()
        for index in range(0, len(chunks), group_size)
    ]

    return merged_chunks[:limit]


@method_decorator(csrf_exempt, name='dispatch')
class LearningUnitListCreateView(generics.ListCreateAPIView):
    serializer_class = LearningUnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningUnit.objects.filter(owner=self.request.user).annotate(
            generated_flashcards_count=Count('flashcards')
        )

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LearningUnitDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = LearningUnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningUnit.objects.filter(owner=self.request.user).annotate(
            generated_flashcards_count=Count('flashcards')
        )


@method_decorator(csrf_exempt, name='dispatch')
class GenerateFlashCardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        learning_unit = get_object_or_404(LearningUnit, pk=pk, owner=request.user)
        chunks = split_into_flashcard_chunks(learning_unit.raw_content)
        chunks = merge_chunks_to_limit(chunks, learning_unit.max_flashcards)
        flashcard_pairs = [build_question_answer_pair(chunk) for chunk in chunks]
        flashcard_pairs = [pair for pair in flashcard_pairs if pair and pair['answer']]

        if not flashcard_pairs:
            return Response(
                {'detail': 'No flashcards could be generated from the provided content.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            learning_unit.flashcards.all().delete()
            flashcards = [
                FlashCard(
                    learning_unit=learning_unit,
                    question=pair['question'],
                    answer=pair['answer'],
                    content=pair['content'],
                    order=index,
                )
                for index, pair in enumerate(flashcard_pairs, start=1)
            ]
            FlashCard.objects.bulk_create(flashcards)

        serializer = FlashCardSerializer(learning_unit.flashcards.all(), many=True)
        return Response(
            {
                'learning_unit_id': learning_unit.id,
                'title': learning_unit.title,
                'max_flashcards': learning_unit.max_flashcards,
                'flashcards': serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name='dispatch')
class ReviewFlashCardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        learning_unit = get_object_or_404(LearningUnit, pk=pk, owner=request.user)
        serializer = ReviewFlashCardsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        flashcard_payload = serializer.validated_data['flashcards']
        if len(flashcard_payload) > learning_unit.max_flashcards:
            return Response(
                {
                    'detail': (
                        f'You can keep at most {learning_unit.max_flashcards} cards for this deck.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            learning_unit.flashcards.all().delete()
            reviewed_flashcards = [
                FlashCard(
                    learning_unit=learning_unit,
                    question=card['question'],
                    answer=card['answer'],
                    content=card.get('content') or f"{card['question']} {card['answer']}",
                    order=index,
                )
                for index, card in enumerate(flashcard_payload, start=1)
            ]
            FlashCard.objects.bulk_create(reviewed_flashcards)

        response_serializer = FlashCardSerializer(learning_unit.flashcards.all(), many=True)
        return Response(
            {
                'learning_unit_id': learning_unit.id,
                'title': learning_unit.title,
                'max_flashcards': learning_unit.max_flashcards,
                'flashcards': response_serializer.data,
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class MarkLearningUnitStudiedView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        learning_unit = get_object_or_404(LearningUnit, pk=pk, owner=request.user)
        learning_unit.last_studied_at = timezone.now()
        learning_unit.save(update_fields=['last_studied_at', 'updated_at'])
        serializer = LearningUnitSerializer(learning_unit)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FlashCardListView(generics.ListAPIView):
    serializer_class = FlashCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        learning_unit = get_object_or_404(
            LearningUnit,
            pk=self.kwargs['pk'],
            owner=self.request.user,
        )
        return learning_unit.flashcards.all()


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        return Response(
            {
                'token': token.key,
                'user': UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = AuthToken.objects.get_or_create(user=user)
        if not created:
            token.rotate()

        return Response(
            {
                'token': token.key,
                'user': UserSerializer(user).data,
            }
        )


class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response({'user': UserSerializer(request.user).data})


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if hasattr(request.user, 'auth_token'):
            request.user.auth_token.delete()
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)

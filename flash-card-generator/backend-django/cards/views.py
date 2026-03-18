import re

from django.contrib.auth import logout
from django.db import transaction
from django.shortcuts import get_object_or_404
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
    UserSerializer,
)


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
        words = paragraph.split()
        if len(words) <= max_words:
            if len(words) >= 5:
                chunks.append(paragraph)
            continue

        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
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
        return LearningUnit.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LearningUnitDetailView(generics.RetrieveAPIView):
    serializer_class = LearningUnitSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LearningUnit.objects.filter(owner=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class GenerateFlashCardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        learning_unit = get_object_or_404(LearningUnit, pk=pk, owner=request.user)
        chunks = split_into_flashcard_chunks(learning_unit.raw_content)
        chunks = merge_chunks_to_limit(chunks, learning_unit.max_flashcards)

        if not chunks:
            return Response(
                {'detail': 'No flashcards could be generated from the provided content.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            learning_unit.flashcards.all().delete()
            flashcards = [
                FlashCard(
                    learning_unit=learning_unit,
                    content=chunk,
                    order=index,
                )
                for index, chunk in enumerate(chunks, start=1)
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

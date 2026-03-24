from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import AuthToken, FlashCard, LearningUnit


MAX_FLASHCARDS_LIMIT = 20
User = get_user_model()


class FlashCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashCard
        fields = ['id', 'question', 'answer', 'content', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class ReviewFlashCardInputSerializer(serializers.Serializer):
    question = serializers.CharField()
    answer = serializers.CharField()
    content = serializers.CharField(required=False, allow_blank=True)

    def validate_question(self, value):
        normalized_value = value.strip()
        if not normalized_value:
            raise serializers.ValidationError('Question cannot be blank.')
        return normalized_value

    def validate_answer(self, value):
        normalized_value = value.strip()
        if not normalized_value:
            raise serializers.ValidationError('Answer cannot be blank.')
        return normalized_value

    def validate_content(self, value):
        return value.strip()


class ReviewFlashCardsSerializer(serializers.Serializer):
    flashcards = ReviewFlashCardInputSerializer(many=True)

    def validate_flashcards(self, value):
        if not value:
            raise serializers.ValidationError('Keep at least one card before finishing the deck.')
        return value


class LearningUnitSerializer(serializers.ModelSerializer):
    flashcards = FlashCardSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    generated_flashcards_count = serializers.SerializerMethodField()

    def get_generated_flashcards_count(self, obj):
        annotated_count = getattr(obj, 'generated_flashcards_count', None)
        if annotated_count is not None:
            return annotated_count
        return obj.flashcards.count()

    def validate_max_flashcards(self, value):
        if value < 1 or value > MAX_FLASHCARDS_LIMIT:
            raise serializers.ValidationError(
                f'Max flashcards must be between 1 and {MAX_FLASHCARDS_LIMIT}.'
            )
        return value

    class Meta:
        model = LearningUnit
        fields = [
            'id',
            'title',
            'raw_content',
            'max_flashcards',
            'last_studied_at',
            'owner_username',
            'generated_flashcards_count',
            'created_at',
            'updated_at',
            'flashcards',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'flashcards']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id', 'username']


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        normalized_value = value.strip()

        if not normalized_value:
            raise serializers.ValidationError('Username cannot be blank.')

        if User.objects.filter(username__iexact=normalized_value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return normalized_value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
        )
        token = AuthToken.objects.create(user=user)
        return user, token


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        normalized_username = attrs['username'].strip()

        if not normalized_username:
            raise serializers.ValidationError('Username cannot be blank.')

        try:
            user = User.objects.get(username__iexact=normalized_username)
        except User.DoesNotExist:
            user = None

        if not user or not user.check_password(attrs['password']):
            raise serializers.ValidationError('Invalid username or password.')

        attrs['user'] = user
        attrs['username'] = normalized_username
        return attrs

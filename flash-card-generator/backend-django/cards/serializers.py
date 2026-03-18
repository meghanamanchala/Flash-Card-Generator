from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import AuthToken, FlashCard, LearningUnit


MAX_FLASHCARDS_LIMIT = 20
User = get_user_model()


class FlashCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashCard
        fields = ['id', 'content', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class LearningUnitSerializer(serializers.ModelSerializer):
    flashcards = FlashCardSerializer(many=True, read_only=True)
    owner_username = serializers.CharField(source='owner.username', read_only=True)

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
            'owner_username',
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
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('A user with that username already exists.')
        return value

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
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Invalid username or password.')
        attrs['user'] = user
        return attrs

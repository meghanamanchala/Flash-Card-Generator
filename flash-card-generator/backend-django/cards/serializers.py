from rest_framework import serializers

from .models import FlashCard, LearningUnit


class FlashCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashCard
        fields = ['id', 'content', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class LearningUnitSerializer(serializers.ModelSerializer):
    flashcards = FlashCardSerializer(many=True, read_only=True)

    class Meta:
        model = LearningUnit
        fields = ['id', 'title', 'raw_content', 'created_at', 'updated_at', 'flashcards']
        read_only_fields = ['id', 'created_at', 'updated_at', 'flashcards']

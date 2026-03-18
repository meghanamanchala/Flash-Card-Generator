from rest_framework import serializers

from .models import FlashCard, LearningUnit


MAX_FLASHCARDS_LIMIT = 20


class FlashCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlashCard
        fields = ['id', 'content', 'order', 'created_at']
        read_only_fields = ['id', 'created_at']


class LearningUnitSerializer(serializers.ModelSerializer):
    flashcards = FlashCardSerializer(many=True, read_only=True)

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
            'created_at',
            'updated_at',
            'flashcards',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'flashcards']

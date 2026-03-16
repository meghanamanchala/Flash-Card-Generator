from django.db import models


class LearningUnit(models.Model):
    title = models.CharField(max_length=255)
    raw_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class FlashCard(models.Model):
    learning_unit = models.ForeignKey(
        LearningUnit,
        on_delete=models.CASCADE,
        related_name='flashcards',
    )
    content = models.TextField()
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('learning_unit', 'order')

    def __str__(self):
        return f'{self.learning_unit.title} - Card {self.order}'

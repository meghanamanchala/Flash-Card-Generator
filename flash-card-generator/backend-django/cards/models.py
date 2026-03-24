import secrets

from django.conf import settings
from django.db import models


class LearningUnit(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='learning_units',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=255)
    raw_content = models.TextField()
    max_flashcards = models.PositiveIntegerField(default=10)
    last_studied_at = models.DateTimeField(null=True, blank=True)
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
    question = models.TextField(blank=True, default='')
    answer = models.TextField(blank=True, default='')
    content = models.TextField()
    order = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'id']
        unique_together = ('learning_unit', 'order')

    def __str__(self):
        return f'{self.learning_unit.title} - Card {self.order}'


class AuthToken(models.Model):
    key = models.CharField(max_length=64, unique=True, editable=False)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='auth_token',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def rotate(self):
        self.key = secrets.token_hex(32)
        self.save(update_fields=['key', 'updated_at'])

    def __str__(self):
        return f'Token for {self.user.username}'

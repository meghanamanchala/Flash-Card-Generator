from django.urls import path

from .views import FlashCardListView, GenerateFlashCardsView, LearningUnitCreateView

urlpatterns = [
    path('learning-units/', LearningUnitCreateView.as_view(), name='learning-unit-create'),
    path(
        'learning-units/<int:pk>/generate-cards/',
        GenerateFlashCardsView.as_view(),
        name='generate-flashcards',
    ),
    path(
        'learning-units/<int:pk>/cards/',
        FlashCardListView.as_view(),
        name='learning-unit-cards',
    ),
]

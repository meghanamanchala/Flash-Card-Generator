from django.urls import path

from .views import (
    FlashCardListView,
    GenerateFlashCardsView,
    LearningUnitDetailView,
    LearningUnitListCreateView,
)

urlpatterns = [
    path('learning-units/', LearningUnitListCreateView.as_view(), name='learning-unit-list-create'),
    path('learning-units/<int:pk>/', LearningUnitDetailView.as_view(), name='learning-unit-detail'),
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

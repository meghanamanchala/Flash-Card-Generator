from django.urls import path

from .views import (
    CurrentUserView,
    FlashCardListView,
    GenerateFlashCardsView,
    LearningUnitDetailView,
    LearningUnitListCreateView,
    LoginView,
    MarkLearningUnitStudiedView,
    LogoutView,
    RegisterView,
    ReviewFlashCardsView,
)

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='auth-register'),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/me/', CurrentUserView.as_view(), name='auth-me'),
    path('auth/logout/', LogoutView.as_view(), name='auth-logout'),
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
    path(
        'learning-units/<int:pk>/mark-studied/',
        MarkLearningUnitStudiedView.as_view(),
        name='learning-unit-mark-studied',
    ),
    path(
        'learning-units/<int:pk>/review-cards/',
        ReviewFlashCardsView.as_view(),
        name='review-flashcards',
    ),
]

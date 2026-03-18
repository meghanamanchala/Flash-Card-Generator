from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import AuthToken, LearningUnit

User = get_user_model()


class AuthenticationFlowTests(APITestCase):
    def test_user_can_register_and_receive_token(self):
        response = self.client.post(
            '/api/auth/register/',
            {'username': 'learner', 'password': 'StrongPass123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'learner')

    def test_learning_units_require_authentication(self):
        response = self.client.get('/api/learning-units/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_only_sees_owned_learning_units(self):
        owner = User.objects.create_user(username='owner', password='StrongPass123!')
        other_user = User.objects.create_user(username='other', password='StrongPass123!')
        token = AuthToken.objects.create(user=owner)

        LearningUnit.objects.create(
            owner=owner,
            title='Owned deck',
            raw_content='Some detailed content that is long enough for the serializer.',
            max_flashcards=5,
        )
        LearningUnit.objects.create(
            owner=other_user,
            title='Other deck',
            raw_content='Different content that should not be visible to the first user.',
            max_flashcards=5,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.get('/api/learning-units/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Owned deck')

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

    def test_register_trims_username(self):
        response = self.client.post(
            '/api/auth/register/',
            {'username': '  learner  ', 'password': 'StrongPass123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'learner')

    def test_user_can_login_case_insensitively(self):
        User.objects.create_user(username='Learner', password='StrongPass123!')

        response = self.client.post(
            '/api/auth/login/',
            {'username': ' learner ', 'password': 'StrongPass123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'Learner')

    def test_learning_units_require_authentication(self):
        response = self.client.get('/api/learning-units/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_generate_cards_returns_question_and_answer_fields(self):
        user = User.objects.create_user(username='generator', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Biology',
            raw_content=(
                'Mitochondria are organelles that generate most of the cell ATP supply. '
                'Ribosomes help build proteins from genetic instructions.'
            ),
            max_flashcards=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.post(
            f'/api/learning-units/{learning_unit.id}/generate-cards/',
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['flashcards']), 2)
        self.assertTrue(response.data['flashcards'][0]['question'].endswith('?'))
        self.assertTrue(response.data['flashcards'][0]['answer'])

    def test_generate_cards_handles_stands_for_and_because_patterns(self):
        user = User.objects.create_user(username='patterns', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Biology terms',
            raw_content=(
                'ATP stands for adenosine triphosphate. '
                'Mitochondria are known as the powerhouses of the cell because they generate ATP.'
            ),
            max_flashcards=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.post(
            f'/api/learning-units/{learning_unit.id}/generate-cards/',
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['flashcards'][0]['question'], 'What does ATP stand for?')
        self.assertEqual(response.data['flashcards'][0]['answer'], 'adenosine triphosphate.')
        self.assertTrue(response.data['flashcards'][1]['question'].startswith('Why are Mitochondria'))
        self.assertTrue(response.data['flashcards'][1]['answer'].startswith('Because'))

    def test_generate_cards_cleans_discourse_prefixes_and_question_passages(self):
        user = User.objects.create_user(username='cleanup', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Strategy',
            raw_content=(
                'Now, your first action is to define the core constraint before proposing a solution. '
                'A great engineer can solve complex technical issues but still struggle with burnout. '
                'Why does technical excellence fail to prevent personal disaster?'
            ),
            max_flashcards=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.post(
            f'/api/learning-units/{learning_unit.id}/generate-cards/',
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['flashcards'][0]['question'], 'What is your first action?')
        self.assertTrue(response.data['flashcards'][1]['question'].startswith('Why does technical excellence'))
        self.assertIn('burnout', response.data['flashcards'][1]['answer'])

    def test_generate_cards_handles_structures_and_stage_lists(self):
        user = User.objects.create_user(username='biology-lists', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Mitochondria details',
            raw_content=(
                'The structure of mitochondria includes an outer membrane, '
                'an inner membrane with folds called cristae, an intermembrane space, and a matrix. '
                'Cellular respiration occurs in three main stages: glycolysis (cytoplasm), '
                'citric acid cycle (mitochondrial matrix), and oxidative phosphorylation (inner membrane).'
            ),
            max_flashcards=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.post(
            f'/api/learning-units/{learning_unit.id}/generate-cards/',
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data['flashcards'][0]['question'],
            'What are the four structural components of mitochondria?',
        )
        self.assertIn('1. an outer membrane', response.data['flashcards'][0]['answer'])
        self.assertEqual(
            response.data['flashcards'][1]['question'],
            'What are the three main stages of Cellular respiration?',
        )
        self.assertIn(
            '3. oxidative phosphorylation (inner membrane)',
            response.data['flashcards'][1]['answer'],
        )

    def test_generate_cards_handles_location_and_responsibility_patterns(self):
        user = User.objects.create_user(username='biology-locations', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Cell notes',
            raw_content=(
                'Glycolysis occurs in the cytoplasm. '
                'The nucleus is responsible for storing genetic information.'
            ),
            max_flashcards=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.post(
            f'/api/learning-units/{learning_unit.id}/generate-cards/',
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['flashcards'][0]['question'], 'Where does Glycolysis occur?')
        self.assertEqual(response.data['flashcards'][0]['answer'], 'the cytoplasm.')
        self.assertEqual(
            response.data['flashcards'][1]['question'],
            'What is the nucleus responsible for?',
        )
        self.assertEqual(response.data['flashcards'][1]['answer'], 'storing genetic information.')

    def test_user_only_sees_owned_learning_units(self):
        owner = User.objects.create_user(username='owner', password='StrongPass123!')
        other_user = User.objects.create_user(username='other', password='StrongPass123!')
        token = AuthToken.objects.create(user=owner)

        owned_deck = LearningUnit.objects.create(
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

        owned_deck.flashcards.create(
            question='What is the owned fact?',
            answer='It belongs to the owner.',
            content='It belongs to the owner.',
            order=1,
        )
        owned_deck.flashcards.create(
            question='What is the second owned fact?',
            answer='There are two owned cards.',
            content='There are two owned cards.',
            order=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.get('/api/learning-units/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Owned deck')
        self.assertEqual(response.data[0]['generated_flashcards_count'], 2)

    def test_review_cards_replaces_generated_cards_with_kept_set(self):
        user = User.objects.create_user(username='reviewer', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Biology review',
            raw_content='Mitochondria generate ATP. Ribosomes build proteins.',
            max_flashcards=3,
        )

        learning_unit.flashcards.create(
            question='What do mitochondria do?',
            answer='They generate ATP.',
            content='Mitochondria generate ATP.',
            order=1,
        )
        learning_unit.flashcards.create(
            question='What do ribosomes do?',
            answer='They build proteins.',
            content='Ribosomes build proteins.',
            order=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.post(
            f'/api/learning-units/{learning_unit.id}/review-cards/',
            {
                'flashcards': [
                    {
                        'question': 'Why are mitochondria important?',
                        'answer': 'They generate ATP for the cell.',
                        'content': 'Mitochondria are important because they generate ATP.',
                    }
                ]
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['flashcards']), 1)
        self.assertEqual(response.data['flashcards'][0]['question'], 'Why are mitochondria important?')
        self.assertEqual(learning_unit.flashcards.count(), 1)
        self.assertEqual(learning_unit.flashcards.first().answer, 'They generate ATP for the cell.')

    def test_review_cards_requires_at_least_one_kept_card(self):
        user = User.objects.create_user(username='empty-review', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Empty review',
            raw_content='This content is long enough to create a deck for review.',
            max_flashcards=2,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.post(
            f'/api/learning-units/{learning_unit.id}/review-cards/',
            {'flashcards': []},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('flashcards', response.data)

    def test_user_can_delete_owned_learning_unit(self):
        user = User.objects.create_user(username='deleter', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Delete me',
            raw_content='This deck has enough content to be valid and removable.',
            max_flashcards=4,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.delete(f'/api/learning-units/{learning_unit.id}/')

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(LearningUnit.objects.filter(id=learning_unit.id).exists())

    def test_learning_unit_defaults_to_not_studied(self):
        user = User.objects.create_user(username='library', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Fresh deck',
            raw_content='This is a fresh deck with enough content to appear in the library.',
            max_flashcards=4,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.get('/api/learning-units/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], learning_unit.id)
        self.assertIsNone(response.data[0]['last_studied_at'])

    def test_mark_learning_unit_studied_updates_timestamp(self):
        user = User.objects.create_user(username='studier', password='StrongPass123!')
        token = AuthToken.objects.create(user=user)
        learning_unit = LearningUnit.objects.create(
            owner=user,
            title='Study me',
            raw_content='This deck contains enough content to be opened and marked as studied.',
            max_flashcards=4,
        )

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.key}')
        response = self.client.post(f'/api/learning-units/{learning_unit.id}/mark-studied/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        learning_unit.refresh_from_db()
        self.assertIsNotNone(learning_unit.last_studied_at)
        self.assertEqual(response.data['id'], learning_unit.id)

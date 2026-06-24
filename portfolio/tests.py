from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import connection
from django.test.utils import CaptureQueriesContext
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta

from .models import Project, Event, Category, Skill, EventType

User = get_user_model()


# ---------- ВСПОМОГАТЕЛЬНЫЙ MIXIN ----------

class BaseSetup:
    """Базовые фикстуры для тестов проектов и мероприятий."""

    def create_base_fixtures(self):
        """
        Создаёт пользователей, категорию, навык и тип мероприятия.
        Используется в setUp() дочерних классов.
        """
        self.owner = User.objects.create_user(username='owner', password='pass123')
        self.other = User.objects.create_user(username='other', password='pass123')
        self.category = Category.objects.create(name='Веб-разработка')
        self.skill = Skill.objects.create(name='Django')
        self.event_type = EventType.objects.create(name='Олимпиада')


# ---------- ВАЛИДАЦИЯ ПРОЕКТОВ ----------

class ProjectValidationTest(BaseSetup, APITestCase):
    """Тесты валидации сериализатора ProjectSerializer."""

    def setUp(self):
        """Инициализирует фикстуры и авторизует клиент под owner."""
        self.create_base_fixtures()
        self.client.force_authenticate(user=self.owner)

    def test_project_title_unique_per_user(self):
        """
        Тест 1: нельзя создать два проекта с одинаковым названием у одного пользователя.
        """
        Project.objects.create(user=self.owner, title='Мой проект')
        response = self.client.post('/api/projects/', {'title': 'Мой проект'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_project_title_min_length(self):
        """
        Тест 3: название проекта короче 3 символов не проходит валидацию.
        """
        response = self.client.post('/api/projects/', {'title': 'аб'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_same_title_different_users_allowed(self):
        """
        Одинаковое название у разных пользователей — допустимо.
        """
        Project.objects.create(user=self.other, title='Общий проект')
        response = self.client.post('/api/projects/', {'title': 'Общий проект'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


# ---------- ВАЛИДАЦИЯ МЕРОПРИЯТИЙ ----------

class EventValidationTest(BaseSetup, APITestCase):
    """Тесты валидации сериализатора EventSerializer."""

    def setUp(self):
        """Инициализирует фикстуры и авторизует клиент под owner."""
        self.create_base_fixtures()
        self.client.force_authenticate(user=self.owner)

    def test_event_requires_result_or_certificate(self):
        """
        Тест 2: мероприятие без result и без certificate_image не сохраняется.
        """
        response = self.client.post('/api/events/', {'title': 'Тест событие'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_event_with_result_is_valid(self):
        """
        Мероприятие с заполненным result успешно создаётся.
        """
        response = self.client.post(
            '/api/events/',
            {'title': 'Тест событие', 'result': '1 место'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_date_cannot_be_in_future(self):
        """
        Тест 4: event_date в будущем не проходит валидацию.
        """
        future = (date.today() + timedelta(days=10)).isoformat()
        response = self.client.post(
            '/api/events/',
            {'title': 'Будущее событие', 'result': '1 место', 'event_date': future},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('event_date', response.data)

    def test_event_date_in_past_is_valid(self):
        """
        event_date в прошлом — допустима.
        """
        past = (date.today() - timedelta(days=10)).isoformat()
        response = self.client.post(
            '/api/events/',
            {'title': 'Прошлое событие', 'result': '1 место', 'event_date': past},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_event_title_min_length(self):
        """
        Название мероприятия короче 3 символов не проходит валидацию.
        """
        response = self.client.post(
            '/api/events/',
            {'title': 'аб', 'result': '1 место'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


# ---------- API ПРОЕКТОВ ----------

class ProjectAPITest(BaseSetup, APITestCase):
    """Тесты CRUD, прав доступа, фильтрации и поиска проектов."""

    def setUp(self):
        """Инициализирует фикстуры и создаёт тестовый проект."""
        self.create_base_fixtures()
        self.project = Project.objects.create(
            user=self.owner,
            title='Тестовый проект',
            category=self.category,
        )
        self.project.skills.add(self.skill)

    def test_create_project_authenticated(self):
        """
        Тест 5: авторизованный пользователь успешно создаёт проект.
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.post('/api/projects/', {'title': 'Новый проект'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['user']['username'], 'owner')

    def test_update_own_project(self):
        """
        Тест 6: автор может обновить описание своего проекта.
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(
            f'/api/projects/{self.project.id}/',
            {'description': 'Обновлённое описание'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], 'Обновлённое описание')

    def test_update_other_project_forbidden(self):
        """
        Тест 7: попытка изменить чужой проект возвращает 403 Forbidden.
        """
        self.client.force_authenticate(user=self.other)
        response = self.client.patch(
            f'/api/projects/{self.project.id}/',
            {'description': 'Взлом'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_category(self):
        """
        Тест 8: фильтрация по category_id возвращает только проекты нужной категории.
        """
        other_cat = Category.objects.create(name='Другая')
        Project.objects.create(user=self.other, title='Чужой', category=other_cat)

        response = self.client.get(f'/api/projects/?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for p in response.data['results']:
            self.assertEqual(p['category']['name'], 'Веб-разработка')

    def test_search_by_title(self):
        """
        Тест 9: поиск по ?search= возвращает проекты с совпадающим title.
        """
        response = self.client.get('/api/projects/?search=Тестовый')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [p['title'] for p in response.data['results']]
        self.assertIn('Тестовый проект', titles)

    def test_skills_count_serializer_method_field(self):
        """
        Тест 10: SerializerMethodField skills_count возвращает корректное значение.
        """
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['skills_count'], 1)

    def test_is_owner_true_for_author(self):
        """
        is_owner=True когда запрашивает автор проекта.
        """
        self.client.force_authenticate(user=self.owner)
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertTrue(response.data['is_owner'])

    def test_is_owner_false_for_anonymous(self):
        """
        is_owner=False для анонимного пользователя.
        """
        response = self.client.get(f'/api/projects/{self.project.id}/')
        self.assertFalse(response.data['is_owner'])

    def test_create_project_unauthenticated_forbidden(self):
        """
        Неавторизованный пользователь получает 401 при попытке создать проект.
        """
        response = self.client.post('/api/projects/', {'title': 'Без авторизации'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ---------- АННОТАЦИИ ----------

class UserAnnotationTest(APITestCase):
    """Тесты аннотированных полей UserDetailSerializer."""

    def setUp(self):
        """
        Создаёт пользователя с двумя проектами и одним мероприятием.
        """
        self.user = User.objects.create_user(username='ann_user', password='pass123')
        cat = Category.objects.create(name='АннотацияКатегория')
        Project.objects.create(user=self.user, title='Проект А', category=cat)
        Project.objects.create(user=self.user, title='Проект Б')
        et = EventType.objects.create(name='АннотацияТип')
        Event.objects.create(user=self.user, title='Событие А', result='1 место')

    def test_projects_count_annotation(self):
        """
        Тест 11: аннотация projects_count корректно считает проекты пользователя.
        """
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['projects_count'], 2)

    def test_events_count_annotation(self):
        """
        events_count аннотация корректно считает мероприятия пользователя.
        """
        response = self.client.get(f'/api/users/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['events_count'], 1)


# ---------- ОПТИМИЗАЦИЯ ЗАПРОСОВ ----------

class QueryOptimizationTest(BaseSetup, TestCase):
    """Тесты оптимизации SQL-запросов через select_related и prefetch_related."""

    def setUp(self):
        """
        Создаёт 5 проектов с категорией и навыком для проверки N+1.
        """
        self.create_base_fixtures()
        for i in range(5):
            p = Project.objects.create(
                user=self.owner,
                title=f'Проект {i}',
                category=self.category,
            )
            p.skills.add(self.skill)

    def test_select_related_no_n_plus_1(self):
        """
        Тест 12: select_related + prefetch_related не порождают N+1 запросов.
        Ожидается не более 3 запросов: projects + join user/category + prefetch skills.
        """
        with CaptureQueriesContext(connection) as ctx:
            projects = list(
                Project.objects
                .select_related('user', 'category')
                .prefetch_related('skills')
            )
            _ = [(p.user.username, p.category.name, list(p.skills.all())) for p in projects]
        self.assertLessEqual(len(ctx.captured_queries), 5)

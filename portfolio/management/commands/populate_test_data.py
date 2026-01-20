from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from portfolio.models import Category, Skill, Project, EventType, Event
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными для портфолио студентов'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Количество пользователей для создания'
        )
        parser.add_argument(
            '--projects',
            type=int,
            default=10,
            help='Количество проектов для создания'
        )
        parser.add_argument(
            '--events',
            type=int,
            default=10,
            help='Количество мероприятий для создания'
        )

    def handle(self, *args, **options):
        users_count = options['users']
        projects_count = options['projects']
        events_count = options['events']

        self.stdout.write(self.style.WARNING('Начинаем заполнение базы данных...'))

        categories = self._create_categories()
        skills = self._create_skills()
        event_types = self._create_event_types()
        users = self._create_users(users_count)
        self._create_projects(projects_count, users, categories, skills)
        self._create_events(events_count, users, event_types)

        self.stdout.write(self.style.SUCCESS(f'Успешно создано:'))
        self.stdout.write(f'  - Пользователей: {users_count}')
        self.stdout.write(f'  - Категорий: {len(categories)}')
        self.stdout.write(f'  - Навыков: {len(skills)}')
        self.stdout.write(f'  - Проектов: {projects_count}')
        self.stdout.write(f'  - Типов мероприятий: {len(event_types)}')
        self.stdout.write(f'  - Мероприятий: {events_count}')

    def _create_categories(self):
        categories_data = [
            'Веб-разработка',
            'Мобильные приложения',
            'Дизайн',
            'Анализ данных',
            'Машинное обучение',
            'Игровая разработка'
        ]
        categories = []
        for name in categories_data:
            category, created = Category.objects.get_or_create(name=name)
            categories.append(category)
            if created:
                self.stdout.write(f'  Создана категория: {name}')
        return categories

    def _create_skills(self):
        skills_data = [
            'Python', 'JavaScript', 'Django', 'React', 'Vue.js',
            'PostgreSQL', 'Docker', 'Git', 'HTML/CSS', 'TypeScript',
            'Node.js', 'MongoDB', 'FastAPI', 'Flask', 'SQL'
        ]
        skills = []
        for name in skills_data:
            skill, created = Skill.objects.get_or_create(name=name)
            skills.append(skill)
            if created:
                self.stdout.write(f'  Создан навык: {name}')
        return skills

    def _create_event_types(self):
        event_types_data = [
            'Хакатон',
            'Олимпиада',
            'Конференция',
            'Конкурс проектов',
            'Семинар',
            'Воркшоп'
        ]
        event_types = []
        for name in event_types_data:
            event_type, created = EventType.objects.get_or_create(name=name)
            event_types.append(event_type)
            if created:
                self.stdout.write(f'  Создан тип мероприятия: {name}')
        return event_types

    def _create_users(self, count):
        users = []
        for i in range(count):
            username = f'student{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': f'Имя{i+1}',
                    'last_name': f'Фамилия{i+1}',
                    'email': f'{username}@example.com',
                    'role': 'student'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'  Создан пользователь: {username}')
            users.append(user)
        return users

    def _create_projects(self, count, users, categories, skills):
        project_titles = [
            'Интернет-магазин', 'Социальная сеть', 'Блог-платформа',
            'Система управления задачами', 'Портфолио-сайт', 'CRM система',
            'Мобильное приложение для фитнеса', 'Образовательная платформа',
            'Система бронирования', 'Чат-приложение'
        ]

        for i in range(count):
            title = f'{random.choice(project_titles)} {i+1}'
            user = random.choice(users)
            category = random.choice(categories)

            project, created = Project.objects.get_or_create(
                title=title,
                user=user,
                defaults={
                    'description': f'Описание проекта {title}. Реализован с использованием современных технологий.',
                    'category': category,
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 365))
                }
            )

            if created:
                project_skills = random.sample(skills, k=random.randint(2, 5))
                project.skills.set(project_skills)
                self.stdout.write(f'  Создан проект: {title}')

    def _create_events(self, count, users, event_types):
        results = ['1 место', '2 место', '3 место', 'Диплом участника', 'Сертификат участника']

        for i in range(count):
            user = random.choice(users)
            event_type = random.choice(event_types)
            title = f'{event_type.name} по программированию {i+1}'

            event, created = Event.objects.get_or_create(
                title=title,
                user=user,
                defaults={
                    'event_type': event_type,
                    'result': random.choice(results),
                    'created_at': timezone.now() - timedelta(days=random.randint(1, 365))
                }
            )

            if created:
                self.stdout.write(f'  Создано мероприятие: {title}')

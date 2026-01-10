from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator


class User(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Студент'),
        ('teacher', 'Преподаватель'),
        ('admin', 'Администратор'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='Роль'
    )
    photo = models.ImageField(
        upload_to='users/photos/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Фотография профиля',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название категории'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_categories',
        verbose_name='Создал'
    )
    
    class Meta:
        verbose_name = 'Категория проекта'
        verbose_name_plural = 'Категории проектов'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название навыка'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_skills',
        verbose_name='Создал'
    )
    
    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Project(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='Автор проекта'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='projects',
        verbose_name='Категория'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Название проекта'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Описание проекта'
    )
    cover_image = models.ImageField(
        upload_to='projects/covers/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Обложка проекта',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])]
    )
    skills = models.ManyToManyField(
        Skill,
        through='ProjectSkill',
        related_name='projects',
        verbose_name='Навыки'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения'
    )
    
    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.user.get_full_name()})"

    def get_skills_count(self):
        return self.skills.count()
    get_skills_count.short_description = 'Количество навыков'


class ProjectSkill(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='project_skills',
        verbose_name='Проект'
    )
    skill = models.ForeignKey(
        Skill,
        on_delete=models.CASCADE,
        related_name='project_skills',
        verbose_name='Навык'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    
    class Meta:
        verbose_name = 'Навык проекта'
        verbose_name_plural = 'Навыки проектов'
        unique_together = [['project', 'skill']]
        ordering = ['project', 'skill']
    
    def __str__(self):
        return f"{self.project.title} - {self.skill.name}"


class EventType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Название типа'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_event_types',
        verbose_name='Создал'
    )
    
    class Meta:
        verbose_name = 'Тип мероприятия'
        verbose_name_plural = 'Типы мероприятий'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Event(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Участник'
    )
    event_type = models.ForeignKey(
        EventType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        verbose_name='Тип мероприятия'
    )
    title = models.CharField(
        max_length=255,
        verbose_name='Название мероприятия'
    )
    result = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Результат',
        help_text='Например: 1 место, Диплом участника'
    )
    certificate_image = models.ImageField(
        upload_to='events/certificates/%Y/%m/%d/',
        null=True,
        blank=True,
        verbose_name='Изображение сертификата',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'])]
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата изменения'
    )
    
    class Meta:
        verbose_name = 'Участие в мероприятии'
        verbose_name_plural = 'Участия в мероприятиях'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"

    def has_certificate(self):
        return bool(self.certificate_image)
    has_certificate.boolean = True
    has_certificate.short_description = 'Есть сертификат'

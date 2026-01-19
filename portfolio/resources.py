from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget
from django.utils import timezone
from datetime import timedelta
from .models import Project, Event, User, Category, EventType


class ProjectResource(resources.ModelResource):
    user_name = fields.Field(column_name='Автор')
    category_name = fields.Field(column_name='Категория')
    skills_list = fields.Field(column_name='Навыки')

    class Meta:
        model = Project
        fields = ('id', 'title', 'user_name', 'category_name', 'description', 'skills_list', 'created_at', 'updated_at')
        export_order = ('id', 'title', 'user_name', 'category_name', 'description', 'skills_list', 'created_at', 'updated_at')

    def get_export_queryset(self, queryset):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        return queryset.filter(created_at__gte=thirty_days_ago)

    def dehydrate_user_name(self, project):
        return project.user.get_full_name() if project.user else ''

    def dehydrate_category_name(self, project):
        return project.category.name if project.category else 'Без категории'

    def dehydrate_skills_list(self, project):
        skills = project.skills.all()
        return ', '.join([skill.name for skill in skills]) if skills else 'Нет навыков'


class EventResource(resources.ModelResource):
    user_name = fields.Field(column_name='Участник')
    event_type_name = fields.Field(column_name='Тип мероприятия')
    has_certificate = fields.Field(column_name='Наличие сертификата')

    class Meta:
        model = Event
        fields = ('id', 'title', 'user_name', 'event_type_name', 'result', 'has_certificate', 'created_at', 'updated_at')
        export_order = ('id', 'title', 'user_name', 'event_type_name', 'result', 'has_certificate', 'created_at', 'updated_at')

    def get_export_queryset(self, queryset):
        one_year_ago = timezone.now() - timedelta(days=365)
        return queryset.filter(created_at__gte=one_year_ago).exclude(result='')

    def dehydrate_user_name(self, event):
        return event.user.get_full_name() if event.user else ''

    def dehydrate_event_type_name(self, event):
        return event.event_type.name if event.event_type else 'Не указан'

    def dehydrate_has_certificate(self, event):
        return 'Да' if event.certificate_image else 'Нет'

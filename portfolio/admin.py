from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.db.models import Count
from .models import User, Category, Skill, Project, ProjectSkill, EventType, Event


class ProjectSkillInline(admin.TabularInline):
    model = ProjectSkill
    extra = 1
    verbose_name = 'Навык'
    verbose_name_plural = 'Навыки проекта'
    raw_id_fields = ['skill']
    autocomplete_fields = ['skill']


class ProjectInline(admin.StackedInline):
    model = Project
    extra = 0
    fields = ['title', 'category', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True
    verbose_name = 'Проект'
    verbose_name_plural = 'Проекты пользователя'


class EventInline(admin.TabularInline):
    model = Event
    extra = 0
    fields = ['title', 'event_type', 'result', 'created_at']
    readonly_fields = ['created_at']
    show_change_link = True
    verbose_name = 'Мероприятие'
    verbose_name_plural = 'Мероприятия пользователя'


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        'username',
        'get_full_name_display',
        'email',
        'role',
        'get_projects_count',
        'get_events_count',
        'is_active',
        'date_joined'
    ]
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    inlines = [ProjectInline, EventInline]
    date_hierarchy = 'date_joined'
    list_display_links = ['username', 'get_full_name_display']
    readonly_fields = ['date_joined', 'last_login']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'last_name', 'email', 'photo')}),
        ('Роль в системе', {'fields': ('role',)}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    filter_horizontal = ['groups', 'user_permissions']

    @admin.display(description='ФИО', ordering='last_name')
    def get_full_name_display(self, obj):
        return obj.get_full_name() or obj.username

    @admin.display(description='Проектов')
    def get_projects_count(self, obj):
        return obj.projects.count()

    @admin.display(description='Мероприятий')
    def get_events_count(self, obj):
        return obj.events.count()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_projects_count', 'created_by', 'created_at']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    list_display_links = ['name']
    raw_id_fields = ['created_by']
    readonly_fields = ['created_at', 'get_projects_count']
    search_fields = ['name']
    fields = ['name', 'created_by', 'created_at', 'get_projects_count']

    @admin.display(description='Количество проектов', ordering='projects_count')
    def get_projects_count(self, obj):
        if hasattr(obj, 'projects_count'):
            return obj.projects_count
        return obj.projects.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(projects_count=Count('projects'))


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_projects_count', 'created_by', 'created_at']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    list_display_links = ['name']
    raw_id_fields = ['created_by']
    readonly_fields = ['created_at', 'get_projects_count']
    search_fields = ['name']
    fields = ['name', 'created_by', 'created_at', 'get_projects_count']

    @admin.display(description='Используется в проектах', ordering='projects_count')
    def get_projects_count(self, obj):
        if hasattr(obj, 'projects_count'):
            return obj.projects_count
        return obj.projects.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(projects_count=Count('projects'))


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'user',
        'category',
        'get_skills_list',
        'has_cover_image',
        'created_at',
        'updated_at'
    ]
    list_filter = ['category', 'created_at', 'updated_at']
    inlines = [ProjectSkillInline]
    date_hierarchy = 'created_at'
    filter_horizontal = ['skills']
    list_display_links = ['title']
    raw_id_fields = ['user', 'category']
    readonly_fields = ['created_at', 'updated_at', 'get_cover_preview']
    search_fields = ['title', 'description', 'user__username', 'user__first_name', 'user__last_name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'category', 'description')
        }),
        ('Навыки', {
            'fields': ('skills',),
            'classes': ('collapse',)
        }),
        ('Изображение', {
            'fields': ('cover_image', 'get_cover_preview')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Навыки')
    def get_skills_list(self, obj):
        skills = obj.skills.all()[:3]
        skills_str = ', '.join([skill.name for skill in skills])
        count = obj.skills.count()
        if count > 3:
            skills_str += f' и еще {count - 3}'
        return skills_str or '-'

    @admin.display(description='Обложка', boolean=True)
    def has_cover_image(self, obj):
        return bool(obj.cover_image)

    @admin.display(description='Превью обложки')
    def get_cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;"/>',
                obj.cover_image.url
            )
        return 'Нет изображения'


@admin.register(ProjectSkill)
class ProjectSkillAdmin(admin.ModelAdmin):
    list_display = ['project', 'skill', 'created_at']
    list_filter = ['created_at', 'skill']
    date_hierarchy = 'created_at'
    list_display_links = ['project', 'skill']
    raw_id_fields = ['project', 'skill']
    readonly_fields = ['created_at']
    search_fields = ['project__title', 'skill__name']
    autocomplete_fields = ['project', 'skill']


@admin.register(EventType)
class EventTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_events_count', 'created_by', 'created_at']
    list_filter = ['created_at']
    date_hierarchy = 'created_at'
    list_display_links = ['name']
    raw_id_fields = ['created_by']
    readonly_fields = ['created_at', 'get_events_count']
    search_fields = ['name']
    fields = ['name', 'created_by', 'created_at', 'get_events_count']

    @admin.display(description='Количество мероприятий', ordering='events_count')
    def get_events_count(self, obj):
        if hasattr(obj, 'events_count'):
            return obj.events_count
        return obj.events.count()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.annotate(events_count=Count('events'))


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'user',
        'event_type',
        'result',
        'has_certificate',
        'created_at',
        'updated_at'
    ]
    list_filter = ['event_type', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    list_display_links = ['title']
    raw_id_fields = ['user', 'event_type']
    readonly_fields = ['created_at', 'updated_at', 'get_certificate_preview']
    search_fields = [
        'title',
        'result',
        'user__username',
        'user__first_name',
        'user__last_name'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'event_type', 'result')
        }),
        ('Сертификат', {
            'fields': ('certificate_image', 'get_certificate_preview')
        }),
        ('Метаданные', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Превью сертификата')
    def get_certificate_preview(self, obj):
        if obj.certificate_image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 300px;"/>',
                obj.certificate_image.url
            )
        return 'Нет сертификата'


admin.site.site_header = 'Администрирование портфолио студентов'
admin.site.site_title = 'Портфолио студентов'
admin.site.index_title = 'Управление системой'

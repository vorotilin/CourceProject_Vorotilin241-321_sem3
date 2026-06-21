import django_filters
from django.db.models import QuerySet
from .models import Project, Event, Skill


class ProjectFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    skills = django_filters.ModelMultipleChoiceFilter(queryset=Skill.objects.all())
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')

    class Meta:
        model = Project
        fields = ['category', 'user', 'title', 'description', 'skills']


class EventFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    result = django_filters.CharFilter(lookup_expr='icontains')
    event_date_after = django_filters.DateFilter(field_name='event_date', lookup_expr='gte')
    event_date_before = django_filters.DateFilter(field_name='event_date', lookup_expr='lte')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    has_certificate = django_filters.BooleanFilter(method='filter_has_certificate')

    class Meta:
        model = Event
        fields = ['event_type', 'user', 'title', 'result']

    def filter_has_certificate(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Фильтрует мероприятия по наличию сертификата.
        Args:
            queryset: Исходный queryset мероприятий
            name: Имя поля фильтра
            value: True — только с сертификатом, False — только без
        """
        if value:
            return queryset.exclude(certificate_image='')
        return queryset.filter(certificate_image='')

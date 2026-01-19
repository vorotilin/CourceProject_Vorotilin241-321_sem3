import django_filters
from .models import Project, Event


class ProjectFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    updated_after = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='gte')
    updated_before = django_filters.DateTimeFilter(field_name='updated_at', lookup_expr='lte')

    class Meta:
        model = Project
        fields = ['category', 'user', 'title', 'description']


class EventFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    result = django_filters.CharFilter(lookup_expr='icontains')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    has_certificate = django_filters.BooleanFilter(method='filter_has_certificate')

    class Meta:
        model = Event
        fields = ['event_type', 'user', 'title', 'result']

    def filter_has_certificate(self, queryset, name, value):
        if value:
            return queryset.exclude(certificate_image='')
        else:
            return queryset.filter(certificate_image='')

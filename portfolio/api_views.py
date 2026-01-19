from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Event, Category, Skill, EventType
from .serializers import (
    ProjectSerializer, EventSerializer, CategorySerializer,
    SkillSerializer, EventTypeSerializer
)
from .filters import ProjectFilter, EventFilter


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Project.objects.all()
        category_id = self.kwargs.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        my_projects = self.request.query_params.get('my_projects', None)
        if my_projects and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'result']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Event.objects.all()
        event_type_id = self.kwargs.get('event_type_id')
        if event_type_id:
            queryset = queryset.filter(event_type_id=event_type_id)

        my_events = self.request.query_params.get('my_events', None)
        if my_events and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class EventTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = EventType.objects.all()
    serializer_class = EventTypeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

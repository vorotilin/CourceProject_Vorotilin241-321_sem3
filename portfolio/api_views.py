from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Project, Event, Category, Skill, EventType
from .serializers import (
    ProjectSerializer, EventSerializer, CategorySerializer,
    SkillSerializer, EventTypeSerializer
)
from .filters import ProjectFilter, EventFilter
from .permissions import IsOwnerOrAdmin


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.select_related('user', 'category').prefetch_related('skills')
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProjectFilter
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Project.objects.select_related('user', 'category').prefetch_related('skills')
        category_id = self.kwargs.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        my_projects = self.request.query_params.get('my_projects', None)
        if my_projects and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['GET'], detail=False)
    def recent_or_updated(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)
        seven_days_ago = timezone.now() - timedelta(days=7)

        queryset = Project.objects.filter(
            (Q(created_at__gte=thirty_days_ago) | Q(updated_at__gte=seven_days_ago)) &
            Q(user=request.user)
        ) if request.user.is_authenticated else Project.objects.none()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def search_complex(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': 'Query parameter q is required'}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Project.objects.filter(
            (Q(title__icontains=query) | Q(description__icontains=query)) &
            ~Q(category__isnull=True)
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def add_skill(self, request, pk=None):
        project = self.get_object()
        skill_id = request.data.get('skill_id')

        if not skill_id:
            return Response({'error': 'skill_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            skill = Skill.objects.get(id=skill_id)
            project.skills.add(skill)
            return Response({'status': 'skill added'}, status=status.HTTP_200_OK)
        except Skill.DoesNotExist:
            return Response({'error': 'Skill not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=True)
    def remove_skill(self, request, pk=None):
        project = self.get_object()
        skill_id = request.data.get('skill_id')

        if not skill_id:
            return Response({'error': 'skill_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            skill = Skill.objects.get(id=skill_id)
            project.skills.remove(skill)
            return Response({'status': 'skill removed'}, status=status.HTTP_200_OK)
        except Skill.DoesNotExist:
            return Response({'error': 'Skill not found'}, status=status.HTTP_404_NOT_FOUND)


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.select_related('user', 'event_type')
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = EventFilter
    search_fields = ['title', 'result']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Event.objects.select_related('user', 'event_type')
        event_type_id = self.kwargs.get('event_type_id')
        if event_type_id:
            queryset = queryset.filter(event_type_id=event_type_id)

        my_events = self.request.query_params.get('my_events', None)
        if my_events and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['GET'], detail=False)
    def with_achievements(self, request):
        one_year_ago = timezone.now() - timedelta(days=365)

        queryset = Event.objects.filter(
            ~Q(certificate_image='') &
            (Q(result__icontains='место') | Q(result__icontains='диплом')) &
            Q(created_at__gte=one_year_ago)
        )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=False)
    def recent_participations(self, request):
        thirty_days_ago = timezone.now() - timedelta(days=30)

        queryset = Event.objects.filter(
            (Q(created_at__gte=thirty_days_ago) | Q(updated_at__gte=thirty_days_ago)) &
            Q(user=request.user) &
            ~Q(event_type__isnull=True)
        ) if request.user.is_authenticated else Event.objects.none()

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def update_result(self, request, pk=None):
        event = self.get_object()
        new_result = request.data.get('result')

        if not new_result:
            return Response({'error': 'result is required'}, status=status.HTTP_400_BAD_REQUEST)

        event.result = new_result
        event.save()
        return Response({'status': 'result updated', 'result': event.result}, status=status.HTTP_200_OK)


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

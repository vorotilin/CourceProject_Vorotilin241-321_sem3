from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ProjectViewSet, EventViewSet, CategoryViewSet,
    SkillViewSet, EventTypeViewSet
)

router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'events', EventViewSet, basename='event')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'event-types', EventTypeViewSet, basename='eventtype')

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.index, name='index'),
    path('projects/', views.ProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ProjectCreateView.as_view(), name='project_create'),
    path('projects/<int:pk>/', views.ProjectDetailView.as_view(), name='project_detail'),
]

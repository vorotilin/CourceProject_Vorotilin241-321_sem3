from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Project

def index(request):
    return render(request, 'portfolio/index.html')

class ProjectListView(ListView):
    model = Project
    template_name = 'portfolio/project_list.html'
    context_object_name = 'projects'
    ordering = ['-created_at']

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from .models import Project
from .forms import ProjectForm

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

class ProjectCreateView(CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'portfolio/project_form.html'
    success_url = reverse_lazy('portfolio:project_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

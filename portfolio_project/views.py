from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Project
from .forms import ProjectForm
from django.contrib.auth import get_user_model
from django.db.models import Count

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

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'portfolio/project_form.html'
    success_url = reverse_lazy('portfolio:project_list')
    login_url = '/admin/login/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Проект успешно создан!')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'portfolio/project_form.html'
    success_url = reverse_lazy('portfolio:project_list')
    login_url = '/admin/login/'

    def form_valid(self, form):
        messages.success(self.request, 'Проект успешно обновлен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'portfolio/project_confirm_delete.html'
    success_url = reverse_lazy('portfolio:project_list')
    login_url = '/admin/login/'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Проект успешно удален!')
        return super().delete(request, *args, **kwargs)
User = get_user_model()


class AuthorListView(ListView):
    model = User
    template_name = 'portfolio/author_list.html'
    context_object_name = 'authors'

    def get_queryset(self):
        return (
            User.objects
            .annotate(projects_count=Count('projects'))
            .filter(projects_count__gt=0)
            .order_by('-projects_count', 'last_name')
        )
class AuthorProjectListView(ListView):
    model = Project
    template_name = 'portfolio/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        self.author = User.objects.get(pk=self.kwargs['author_id'])
        return Project.objects.filter(user=self.author).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        context['is_author_page'] = True
        return context
    
print("VIEWS LOADED")
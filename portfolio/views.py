from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import Project
from .forms import ProjectForm, RegisterForm, LoginForm

def index(request):
    return render(request, 'portfolio/index.html')

@require_http_methods(["POST"])
def register_user(request):
    try:
        data = json.loads(request.body)
        form = RegisterForm(data)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Регистрация прошла успешно!',
                'user': {
                    'username': user.username,
                    'full_name': user.get_full_name(),
                    'role': user.get_role_display()
                }
            })
        else:
            errors = {}
            for field, error_list in form.errors.items():
                errors[field] = [str(e) for e in error_list]
            return JsonResponse({'success': False, 'errors': errors}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'errors': {'general': [str(e)]}}, status=500)

@require_http_methods(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Вход выполнен успешно!',
                'user': {
                    'username': user.username,
                    'full_name': user.get_full_name(),
                    'role': user.get_role_display()
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': {'general': ['Неверное имя пользователя или пароль']}
            }, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'errors': {'general': [str(e)]}}, status=500)

@require_http_methods(["POST"])
def logout_user(request):
    logout(request)
    return JsonResponse({'success': True, 'message': 'Выход выполнен успешно!'})

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

class ProjectUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'portfolio/project_form.html'
    success_url = reverse_lazy('portfolio:project_list')
    login_url = '/admin/login/'

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.user

    def form_valid(self, form):
        messages.success(self.request, 'Проект успешно обновлен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)

class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'portfolio/project_confirm_delete.html'
    success_url = reverse_lazy('portfolio:project_list')
    login_url = '/admin/login/'

    def test_func(self):
        project = self.get_object()
        return self.request.user == project.user

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Проект успешно удален!')
        return super().delete(request, *args, **kwargs)

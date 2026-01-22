from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count
import json

from .models import Project, Event
from .forms import ProjectForm, EventForm, RegisterForm, LoginForm

User = get_user_model()


def index(request):
    return render(request, 'portfolio/index.html')


# ---------- AUTH ----------

@require_http_methods(["POST"])
def register_user(request):
    data = json.loads(request.body)
    form = RegisterForm(data)

    if form.is_valid():
        user = form.save()
        login(request, user)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_http_methods(["POST"])
def login_user(request):
    data = json.loads(request.body)
    user = authenticate(
        request,
        username=data.get('username'),
        password=data.get('password')
    )

    if user:
        login(request, user)
        return JsonResponse({'success': True})

    return JsonResponse({'success': False}, status=400)


@require_http_methods(["POST"])
def logout_user(request):
    logout(request)
    return JsonResponse({'success': True})


# ---------- PROJECTS ----------

from django.views.generic import ListView
from .models import Project, Event

class ProjectListView(ListView):
    model = Project
    template_name = 'portfolio/project_list.html'
    context_object_name = 'projects'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.all().order_by('-created_at')
        context['is_author_page'] = False
        return context



class ProjectDetailView(DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'


class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'portfolio/project_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'portfolio:author_projects',
            kwargs={'author_id': self.request.user.id}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_event'] = False
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Проект успешно создан')
        return super().form_valid(form)


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'portfolio/project_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'portfolio:author_projects',
            kwargs={'author_id': self.request.user.id}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_event'] = False
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Проект успешно обновлён')
        return super().form_valid(form)


class ProjectDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Project
    template_name = 'portfolio/project_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy(
            'portfolio:author_projects',
            kwargs={'author_id': self.request.user.id}
        )

    def test_func(self):
        return self.request.user == self.get_object().user


# ---------- EVENTS ----------

class EventCreateView(LoginRequiredMixin, CreateView):
    model = Event
    form_class = EventForm
    template_name = 'portfolio/project_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'portfolio:author_projects',
            kwargs={'author_id': self.request.user.id}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_event'] = True
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Событие успешно добавлено')
        return super().form_valid(form)

class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Event
    form_class = EventForm
    template_name = 'portfolio/project_form.html'

    def get_success_url(self):
        return reverse_lazy(
            'portfolio:author_projects',
            kwargs={'author_id': self.request.user.id}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_event'] = True
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Событие успешно обновлено')
        return super().form_valid(form)

    def test_func(self):
        return self.request.user == self.get_object().user

class EventListView(ListView):
    model = Event
    template_name = 'portfolio/event_list.html'
    context_object_name = 'events'
    ordering = ['-start_date']  
    paginate_by = 10
class AuthorEventListView(ListView):
    model = Event
    template_name = 'portfolio/author_event_list.html'
    context_object_name = 'events'
    ordering = ['-start_date']
    paginate_by = 10

    def get_queryset(self):
        # self.kwargs['user_id'] — получаем ID пользователя из URL
        user_id = self.kwargs.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                return Event.objects.filter(participants=user).order_by('-start_date')
            except User.DoesNotExist:
                return Event.objects.none()
        return Event.objects.none()

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
        author_id = self.kwargs.get('author_id')
        return Project.objects.filter(user_id=author_id).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author_id = self.kwargs.get('author_id')
        context['events'] = Event.objects.filter(user_id=author_id).order_by('-created_at')
        context['is_author_page'] = True
        context['author'] = context['projects'][0].user if context['projects'] else None
        return context


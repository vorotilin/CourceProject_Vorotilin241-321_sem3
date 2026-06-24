from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import Project, Event, User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'category', 'skills', 'cover_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_title(self):
        value = self.cleaned_data.get('title', '')
        if len(value) < 3:
            raise forms.ValidationError('Название проекта должно содержать минимум 3 символа.')
        return value

    def clean(self):
        cleaned = super().clean()
        title = cleaned.get('title')
        if title and self.user:
            qs = Project.objects.filter(user=self.user, title=title)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('title', 'У вас уже есть проект с таким названием.')
        return cleaned


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'event_type', 'event_date', 'result', 'certificate_image']
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_title(self):
        value = self.cleaned_data.get('title', '')
        if len(value) < 3:
            raise forms.ValidationError('Название мероприятия должно содержать минимум 3 символа.')
        return value

    def clean_event_date(self):
        value = self.cleaned_data.get('event_date')
        if value and value > timezone.now().date():
            raise forms.ValidationError('Дата мероприятия не может быть в будущем.')
        return value

    def clean(self):
        cleaned = super().clean()
        result = cleaned.get('result')
        certificate = cleaned.get('certificate_image')
        existing_certificate = self.instance.certificate_image if self.instance and self.instance.pk else None
        if not result and not certificate and not existing_certificate:
            raise forms.ValidationError('Необходимо указать либо результат участия, либо загрузить сертификат.')
        return cleaned
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Имя пользователя'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Фамилия'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Пароль'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Подтверждение пароля'}),
        }

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Имя пользователя'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))

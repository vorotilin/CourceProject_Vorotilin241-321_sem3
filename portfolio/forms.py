from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'category', 'skills', 'cover_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.CheckboxSelectMultiple(),
        }

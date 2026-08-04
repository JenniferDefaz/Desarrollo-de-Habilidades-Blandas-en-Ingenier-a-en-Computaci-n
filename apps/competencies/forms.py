from django import forms
from .models import Competency, Subcompetency, Rubric

class CompetencyForm(forms.ModelForm):
    class Meta:
        model = Competency
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Comunicación Efectiva'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class SubcompetencyForm(forms.ModelForm):
    class Meta:
        model = Subcompetency
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Comunicación Oral'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class RubricForm(forms.ModelForm):
    class Meta:
        model = Rubric
        fields = ['level', 'description', 'min_score', 'max_score']
        widgets = {
            'level': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'min_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

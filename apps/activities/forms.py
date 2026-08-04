from django import forms
from .models import Activity, ActivityType

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = [
            'title', 'description', 'activity_type', 'competency',
            'instructor', 'max_participants', 'start_date', 'end_date',
            'location', 'is_active'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Taller de Trabajo en Equipo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'activity_type': forms.Select(attrs={'class': 'form-select'}),
            'competency': forms.Select(attrs={'class': 'form-select'}),
            'instructor': forms.Select(attrs={'class': 'form-select'}),
            'max_participants': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Aula 101 o Enlace Zoom/Teams'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instructor' in self.fields:
            self.fields['instructor'].required = False
            self.fields['instructor'].empty_label = "-- Asignar automáticamente a mí --"


from django import forms
from .models import GraduateFeedback


class GraduateFeedbackForm(forms.ModelForm):
    """Formulario para que los graduados registren su retroalimentación laboral."""
    class Meta:
        model = GraduateFeedback
        fields = [
            'company_name', 'job_title', 'competency',
            'relevance_rating', 'frequency_rating', 'feedback_text'
        ]
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Empresa o Institución actual'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Cargo o puesto de trabajo'}),
            'competency': forms.Select(attrs={'class': 'form-select'}),
            'relevance_rating': forms.Select(attrs={'class': 'form-select'}),
            'frequency_rating': forms.Select(attrs={'class': 'form-select'}),
            'feedback_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Comentarios sobre el impacto de esta habilidad blanda en su trabajo...'}),
        }

from django import forms
from .models import Evidence, EvidenceStatus

class EvidenceForm(forms.ModelForm):
    class Meta:
        model = Evidence
        fields = ['title', 'description', 'competency', 'activity', 'evidence_type', 'file', 'external_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Informe de Proyecto Colaborativo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Describe brevemente la evidencia que estás adjuntando...'}),
            'competency': forms.Select(attrs={'class': 'form-select'}),
            'activity': forms.Select(attrs={'class': 'form-select'}),
            'evidence_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'external_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://drive.google.com/... o https://youtube.com/...'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Límite máximo de 50 MB según requerimientos del proyecto
            max_size_bytes = 50 * 1024 * 1024
            if file.size > max_size_bytes:
                raise forms.ValidationError(f'El archivo excede el tamaño máximo permitido de 50 MB (Tamaño actual: {round(file.size / (1024 * 1024), 2)} MB).')
        return file

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')
        external_url = cleaned_data.get('external_url')
        
        if not file and not external_url:
            raise forms.ValidationError('Debes adjuntar un archivo físico o proporcionar un enlace externo.')
            
        return cleaned_data



class ReviewForm(forms.Form):
    status = forms.ChoiceField(
        choices=[
            (EvidenceStatus.APROBADA, 'Aprobar Evidencia'),
            (EvidenceStatus.CORREGIR, 'Solicitar Corrección'),
            (EvidenceStatus.RECHAZADA, 'Rechazar Evidencia')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Resultado de la Revisión'
    )
    review_comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Escribe la retroalimentación cualitativa para el estudiante...'}),
        label='Retroalimentación *',
        required=True
    )

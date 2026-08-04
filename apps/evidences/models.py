from django.conf import settings
from django.db import models


class EvidenceType(models.TextChoices):
    """Tipos de evidencias de aprendizaje aceptados."""
    DOCUMENTO = 'DOCUMENTO', 'Documento PDF / Word'
    PRESENTACION = 'PRESENTACION', 'Presentación'
    VIDEO = 'VIDEO', 'Video'
    IMAGEN = 'IMAGEN', 'Imagen'
    ENLACE_EXTERNO = 'ENLACE_EXTERNO', 'Enlace Externo (Drive/YouTube)'
    OTRO = 'OTRO', 'Otro'


class EvidenceStatus(models.TextChoices):
    """Estados de revisión para una evidencia."""
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    APROBADA = 'APROBADA', 'Aprobada'
    RECHAZADA = 'RECHAZADA', 'Rechazada'
    CORREGIR = 'CORREGIR', 'Solicitar Corrección'


class Evidence(models.Model):
    """Modelo que representa una evidencia de aprendizaje registrada por un estudiante."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evidences',
        verbose_name='Estudiante'
    )
    competency = models.ForeignKey(
        'competencies.Competency',
        on_delete=models.CASCADE,
        related_name='evidences',
        verbose_name='Competencia'
    )
    activity = models.ForeignKey(
        'activities.Activity',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='evidences',
        verbose_name='Actividad Formativa'
    )
    title = models.CharField(max_length=200, verbose_name='Título')
    description = models.TextField(blank=True, verbose_name='Descripción')
    evidence_type = models.CharField(
        max_length=20,
        choices=EvidenceType.choices,
        verbose_name='Tipo de Evidencia'
    )
    file = models.FileField(
        upload_to='evidences/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='Archivo Adjunto'
    )
    external_url = models.URLField(
        blank=True,
        verbose_name='Enlace Externo'
    )
    status = models.CharField(
        max_length=20,
        choices=EvidenceStatus.choices,
        default=EvidenceStatus.PENDIENTE,
        verbose_name='Estado de Revisión'
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_evidences',
        verbose_name='Revisado Por'
    )
    review_comment = models.TextField(blank=True, verbose_name='Retroalimentación')
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Revisión')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Carga')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')

    class Meta:
        db_table = 'evidences_evidence'
        ordering = ['-uploaded_at']
        verbose_name = 'Evidencia'
        verbose_name_plural = 'Evidencias'

    def __str__(self):
        return f'{self.title} - {self.student.get_full_name()}'


class FileMetadata(models.Model):
    """Metadatos del archivo subido como parte de una evidencia."""
    evidence = models.ForeignKey(
        Evidence,
        on_delete=models.CASCADE,
        related_name='files'
    )
    file = models.FileField(upload_to='evidences/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(help_text='Tamaño del archivo en bytes')
    mime_type = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evidences_filemetadata'
        verbose_name = 'Metadato de Archivo'
        verbose_name_plural = 'Metadatos de Archivos'

    def __str__(self):
        return self.original_filename

from django.conf import settings
from django.db import models


class Evaluation360(models.Model):
    """
    Modelo que representa una Evaluación 360° multidireccional.
    Permite evaluar competencias desde distintas perspectivas:
    autoevaluación, pares, docente, empleador y tutor.
    """
    class EvaluationType(models.TextChoices):
        AUTOEVALUACION = 'AUTOEVALUACION', 'Autoevaluación'
        PARES = 'PARES', 'Evaluación por Pares'
        DOCENTE = 'DOCENTE', 'Evaluación por Docente'
        EMPLEADOR = 'EMPLEADOR', 'Evaluación por Empleador'
        TUTOR = 'TUTOR', 'Evaluación por Tutor'

    class Status(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROGRESO = 'EN_PROGRESO', 'En Progreso'
        COMPLETADA = 'COMPLETADA', 'Completada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    competency = models.ForeignKey(
        'competencies.Competency',
        on_delete=models.CASCADE,
        related_name='evaluations',
        verbose_name='Competencia'
    )
    evaluator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations_given',
        verbose_name='Evaluador'
    )
    evaluated = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations_received',
        verbose_name='Evaluado'
    )
    evaluation_type = models.CharField(
        max_length=20,
        choices=EvaluationType.choices,
        verbose_name='Tipo de evaluación'
    )
    period = models.CharField(
        max_length=50,
        verbose_name='Período académico'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDIENTE,
        verbose_name='Estado'
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Fecha límite'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de finalización'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de actualización'
    )

    class Meta:
        db_table = 'evaluations_evaluation360'
        verbose_name = 'Evaluación 360°'
        verbose_name_plural = 'Evaluaciones 360°'

    def __str__(self):
        return f'{self.get_evaluation_type_display()} - {self.evaluated.get_full_name()}'


class EvaluationScore(models.Model):
    """
    Modelo que almacena las puntuaciones individuales por subcompetencia
    asociadas a una Evaluación 360°.
    """
    evaluation = models.ForeignKey(
        Evaluation360,
        on_delete=models.CASCADE,
        related_name='scores',
        verbose_name='Evaluación 360°'
    )
    subcompetency = models.ForeignKey(
        'competencies.Subcompetency',
        on_delete=models.CASCADE,
        verbose_name='Subcompetencia'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Puntuación'
    )
    comment = models.TextField(
        blank=True,
        verbose_name='Comentario'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )

    class Meta:
        db_table = 'evaluations_evaluationscore'
        unique_together = [('evaluation', 'subcompetency')]
        verbose_name = 'Puntuación de Evaluación'
        verbose_name_plural = 'Puntuaciones de Evaluación'

    def __str__(self):
        return f'{self.evaluation} - {self.subcompetency.name}: {self.score}'


class AuditLog(models.Model):
    """
    Historial inmutable APPEND-ONLY para auditoría de acciones del sistema.
    No se permite la modificación ni eliminación de registros existentes.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario'
    )
    action = models.CharField(
        max_length=50,
        verbose_name='Acción'
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name='Nombre del modelo'
    )
    object_id = models.PositiveIntegerField(
        verbose_name='ID del objeto'
    )
    changes = models.JSONField(
        default=dict,
        verbose_name='Cambios realizados'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y hora'
    )

    class Meta:
        db_table = 'evaluations_auditlog'
        ordering = ['-timestamp']
        managed = True
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'

    def __str__(self):
        return f'{self.action} - {self.model_name} #{self.object_id}'

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Los registros de auditoría son inmutables y no se pueden actualizar.")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Los registros de auditoría son inmutables y no se pueden eliminar.")


class GraduateFeedback(models.Model):
    """
    Modelo para la retroalimentación de graduados sobre habilidades blandas en la vida laboral (RF12).
    """
    graduate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='graduate_feedbacks',
        verbose_name='Graduado'
    )
    company_name = models.CharField(
        max_length=200,
        verbose_name='Empresa / Institución de trabajo'
    )
    job_title = models.CharField(
        max_length=150,
        verbose_name='Cargo / Puesto'
    )
    competency = models.ForeignKey(
        'competencies.Competency',
        on_delete=models.CASCADE,
        related_name='graduate_feedbacks',
        verbose_name='Competencia evaluada'
    )
    relevance_rating = models.PositiveSmallIntegerField(
        choices=[(i, f'{i} / 5') for i in range(1, 6)],
        verbose_name='Relevancia en el trabajo (1-5)'
    )
    frequency_rating = models.PositiveSmallIntegerField(
        choices=[(i, f'{i} / 5') for i in range(1, 6)],
        verbose_name='Frecuencia de aplicación (1-5)'
    )
    feedback_text = models.TextField(
        verbose_name='Comentarios / Retroalimentación sobre la competencia'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de registro'
    )

    class Meta:
        db_table = 'evaluations_graduatefeedback'
        ordering = ['-created_at']
        verbose_name = 'Retroalimentación de Graduado'
        verbose_name_plural = 'Retroalimentaciones de Graduados'

    def __str__(self):
        return f"{self.graduate.get_full_name()} - {self.competency.name} ({self.company_name})"


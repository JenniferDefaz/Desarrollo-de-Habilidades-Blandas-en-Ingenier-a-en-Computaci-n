from django.conf import settings
from django.db import models


class CompetencyLevel(models.TextChoices):
    """Niveles de dominio de una competencia para el estudiante."""
    INICIAL = 'INICIAL', 'Inicial'
    EN_DESARROLLO = 'EN_DESARROLLO', 'En Desarrollo'
    COMPETENTE = 'COMPETENTE', 'Competente'
    EXCELENTE = 'EXCELENTE', 'Excelente'


class StudentMetric(models.Model):
    """Métricas agregadas por estudiante para una competencia específica."""
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    competency = models.ForeignKey(
        'competencies.Competency',
        on_delete=models.CASCADE,
        related_name='student_metrics'
    )
    average_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )
    evaluations_count = models.PositiveIntegerField(default=0)
    current_level = models.CharField(
        max_length=20,
        choices=CompetencyLevel.choices,
        default=CompetencyLevel.INICIAL
    )
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analytics_studentmetric'
        unique_together = [('student', 'competency')]
        verbose_name = 'Métrica de Estudiante'
        verbose_name_plural = 'Métricas de Estudiantes'

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.competency.name}: {self.average_score}'


class CohortReport(models.Model):
    """Reportes consolidados por cohorte o grupo académico."""
    title = models.CharField(max_length=200)
    period = models.CharField(
        max_length=50,
        help_text='Período académico'
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    report_data = models.JSONField(
        default=dict,
        help_text='Datos del reporte'
    )
    report_file = models.FileField(
        upload_to='reports/%Y/%m/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'analytics_cohortreport'
        ordering = ['-created_at']
        verbose_name = 'Reporte de Cohorte'
        verbose_name_plural = 'Reportes de Cohortes'

    def __str__(self):
        return f'{self.title} - {self.period}'

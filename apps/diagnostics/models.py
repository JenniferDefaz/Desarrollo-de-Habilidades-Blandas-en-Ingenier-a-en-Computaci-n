from django.conf import settings
from django.db import models


class DiagnosticQuestion(models.Model):
    """Preguntas del cuestionario de diagnóstico."""

    competency = models.ForeignKey(
        'competencies.Competency',
        on_delete=models.CASCADE,
        related_name='diagnostic_questions',
        verbose_name='Competencia'
    )
    text = models.TextField(
        verbose_name='Texto de la pregunta'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='Orden de presentación'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='¿Está activa?'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )

    class Meta:
        db_table = 'diagnostics_diagnosticquestion'
        ordering = ['order']
        verbose_name = 'Pregunta de diagnóstico'
        verbose_name_plural = 'Preguntas de diagnóstico'

    def __str__(self):
        return f'Pregunta {self.order}: {self.text[:50]}'


class DiagnosticResult(models.Model):
    """Resultados del cuestionario de diagnóstico por estudiante."""

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='diagnostic_results',
        verbose_name='Estudiante'
    )
    question = models.ForeignKey(
        DiagnosticQuestion,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Pregunta'
    )
    score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Puntuación asignada'
    )
    observation = models.TextField(
        blank=True,
        verbose_name='Observación adicional'
    )
    evaluated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de evaluación'
    )

    class Meta:
        db_table = 'diagnostics_diagnosticresult'
        unique_together = [('student', 'question')]
        verbose_name = 'Resultado de diagnóstico'
        verbose_name_plural = 'Resultados de diagnóstico'

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.question.text[:30]}'

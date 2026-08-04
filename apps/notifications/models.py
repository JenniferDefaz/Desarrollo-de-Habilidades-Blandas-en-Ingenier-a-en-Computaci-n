from django.conf import settings
from django.db import models


class NotificationType(models.TextChoices):
    """Tipos de notificaciones in-app del sistema."""
    EVALUACION_PENDIENTE = 'EVALUACION_PENDIENTE', 'Evaluación Pendiente'
    ACTIVIDAD_ASIGNADA = 'ACTIVIDAD_ASIGNADA', 'Actividad Asignada'
    EVIDENCIA_REVISADA = 'EVIDENCIA_REVISADA', 'Evidencia Revisada'
    RETROALIMENTACION = 'RETROALIMENTACION', 'Retroalimentación'
    SISTEMA = 'SISTEMA', 'Sistema'


class Notification(models.Model):
    """Modelo para notificaciones in-app dirigidas a usuarios."""
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SISTEMA
    )
    is_read = models.BooleanField(default=False)
    link = models.URLField(
        max_length=500,
        blank=True,
        help_text='Link de acción'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications_notification'
        ordering = ['-created_at']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f'{self.title} → {self.recipient.get_full_name()}'

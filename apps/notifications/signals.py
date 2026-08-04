from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.evidences.models import Evidence, EvidenceStatus
from apps.evaluations.models import Evaluation360
from apps.activities.models import Enrollment, EnrollmentStatus
from .models import Notification, NotificationType


@receiver(post_save, sender=Evidence)
def notify_evidence_review(sender, instance, created, **kwargs):
    """Notifica al estudiante cuando su evidencia es revisada o cambia de estado."""
    if not created and instance.status in [EvidenceStatus.APROBADA, EvidenceStatus.RECHAZADA, EvidenceStatus.CORREGIR]:
        status_display = instance.get_status_display()
        title = f'Evidencia {status_display}: {instance.title}'
        message = f'Tu evidencia "{instance.title}" ha sido evaluada con estado: {status_display}.'
        if instance.review_comment:
            message += f' Retroalimentación: {instance.review_comment}'
            
        Notification.objects.create(
            recipient=instance.student,
            title=title,
            message=message,
            notification_type=NotificationType.EVIDENCIA_REVISADA,
            link='/evidencias/mis-evidencias/'
        )


@receiver(post_save, sender=Evaluation360)
def notify_evaluation_completed(sender, instance, created, **kwargs):
    """Notifica al estudiante evaluado cuando se completa una evaluación 360° o docente."""
    if instance.status == Evaluation360.Status.COMPLETADA:
        # Evitar notificar si se auto-evalúa en diagnóstico para no saturar, pero si es docente/par/empleador notificar.
        if instance.evaluator != instance.evaluated:
            eval_type_display = instance.get_evaluation_type_display()
            title = f'Nueva Evaluación Recibida ({eval_type_display})'
            message = f'Has recibido una evaluación de tipo {eval_type_display} para la competencia "{instance.competency.name if instance.competency else "General"}".'
            
            Notification.objects.create(
                recipient=instance.evaluated,
                title=title,
                message=message,
                notification_type=NotificationType.EVALUACION_PENDIENTE,
                link='/evaluaciones/mi-historial/'
            )


@receiver(post_save, sender=Enrollment)
def notify_activity_enrollment(sender, instance, created, **kwargs):
    """Notifica al estudiante sobre la confirmación de su inscripción a una actividad."""
    if created and instance.status == EnrollmentStatus.INSCRITO:
        Notification.objects.create(
            recipient=instance.student,
            title=f'Inscripción Confirmada: {instance.activity.title}',
            message=f'Te has inscrito exitosamente en la actividad formativa "{instance.activity.title}".',
            notification_type=NotificationType.ACTIVIDAD_ASIGNADA,
            link='/actividades/catalogo/'
        )


@receiver(post_save, sender=Notification)
def dispatch_email_on_notification(sender, instance, created, **kwargs):
    """Envía un correo electrónico SMTP institucional al destinatario cuando se genera una notificación in-app."""
    if created and instance.recipient and instance.recipient.email:
        from .utils import send_notification_email
        send_notification_email(
            recipient_email=instance.recipient.email,
            subject=instance.title,
            message=instance.message
        )


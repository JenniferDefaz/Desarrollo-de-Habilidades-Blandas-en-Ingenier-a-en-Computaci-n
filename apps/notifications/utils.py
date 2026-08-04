from django.core.mail import send_mail
from django.conf import settings
from apps.users.models import SystemSetting


def send_notification_email(recipient_email, subject, message):
    """
    Envía una notificación por correo electrónico institucional respaldada por SystemSetting (SMTP / Configuración Global).
    """
    if not recipient_email:
        return False

    try:
        sys_settings = SystemSetting.get_settings()
        from_email = sys_settings.system_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'notificaciones@sistema.edu.ec')
        
        send_mail(
            subject=f"[Sistema Académico] {subject}",
            message=message,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=True
        )
        return True
    except Exception as e:
        print(f"Error al enviar notificación por correo electrónico: {e}")
        return False

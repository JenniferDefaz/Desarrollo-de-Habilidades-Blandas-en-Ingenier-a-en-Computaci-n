from django.apps import AppConfig


class ActivitiesConfig(AppConfig):
    """
    Configuración de la aplicación de Actividades Formativas.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.activities'
    verbose_name = 'Actividades Formativas'

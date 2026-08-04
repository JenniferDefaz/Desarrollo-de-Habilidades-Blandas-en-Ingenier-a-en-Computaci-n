from django.apps import AppConfig


class CompetenciesConfig(AppConfig):
    """
    Configuración de la aplicación 'competencies' (Gestión de Competencias).
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.competencies'
    verbose_name = 'Gestión de Competencias'

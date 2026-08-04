from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuración de la aplicación de Gestión de Usuarios.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Gestión de Usuarios'

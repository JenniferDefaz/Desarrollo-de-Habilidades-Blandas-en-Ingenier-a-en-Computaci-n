from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.Model):
    """
    Modelo para los roles del sistema RBAC (Control de Acceso Basado en Roles).
    """
    class RoleChoices(models.TextChoices):
        ESTUDIANTE = 'ESTUDIANTE', 'Estudiante'
        DOCENTE = 'DOCENTE', 'Docente'
        TUTOR_ACADEMICO = 'TUTOR_ACADEMICO', 'Tutor Académico'
        COORDINADOR_CARRERA = 'COORDINADOR_CARRERA', 'Coordinador de Carrera'
        EMPRESA_COLABORADORA = 'EMPRESA_COLABORADORA', 'Empresa Colaboradora'
        GRADUADO = 'GRADUADO', 'Graduado'
        BIENESTAR_UNIVERSITARIO = 'BIENESTAR_UNIVERSITARIO', 'Bienestar Universitario'
        ADMINISTRADOR = 'ADMINISTRADOR', 'Administrador'

    # Constantes de clase para fácil acceso a los roles
    ESTUDIANTE = RoleChoices.ESTUDIANTE
    DOCENTE = RoleChoices.DOCENTE
    TUTOR_ACADEMICO = RoleChoices.TUTOR_ACADEMICO
    COORDINADOR_CARRERA = RoleChoices.COORDINADOR_CARRERA
    EMPRESA_COLABORADORA = RoleChoices.EMPRESA_COLABORADORA
    GRADUADO = RoleChoices.GRADUADO
    BIENESTAR_UNIVERSITARIO = RoleChoices.BIENESTAR_UNIVERSITARIO
    ADMINISTRADOR = RoleChoices.ADMINISTRADOR

    name = models.CharField(
        max_length=50,
        unique=True,
        choices=RoleChoices.choices,
        verbose_name='Nombre del rol'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )

    class Meta:
        db_table = 'users_role'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado para el sistema académico.
    Extiende AbstractUser de Django.
    """
    cedula = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Cédula'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name='Rol'
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name='Teléfono'
    )
    institutional_email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
        verbose_name='Correo institucional'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    session_key = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name='Clave de sesión activa'
    )

    class Meta:
        db_table = 'users_customuser'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.username})'


class UserProfile(models.Model):
    """
    Perfil extendido de usuario con información adicional según el rol.
    """
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Usuario'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Biografía'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Avatar'
    )
    career = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Carrera'
    )
    semester = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Semestre actual'
    )
    company_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nombre de la empresa'
    )
    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Año de graduación'
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
        db_table = 'users_userprofile'
        verbose_name = 'Perfil de usuario'
        verbose_name_plural = 'Perfiles de usuario'

    def __str__(self):
        return f'Perfil de {self.user.get_full_name()}'


class SystemSetting(models.Model):
    """
    Modelo para la configuración de parámetros generales de la plataforma.
    """
    max_file_size_mb = models.PositiveIntegerField(
        default=10,
        verbose_name='Límite de tamaño de archivo (MB)'
    )
    allowed_file_extensions = models.CharField(
        max_length=200,
        default='pdf, docx, png, jpg, jpeg, mp4, zip',
        verbose_name='Extensiones permitidas'
    )
    smtp_host = models.CharField(
        max_length=150,
        blank=True,
        default='smtp.gmail.com',
        verbose_name='Servidor SMTP'
    )
    smtp_port = models.PositiveIntegerField(
        default=587,
        verbose_name='Puerto SMTP'
    )
    smtp_use_tls = models.BooleanField(
        default=True,
        verbose_name='Usar TLS para correo'
    )
    system_email = models.EmailField(
        blank=True,
        default='notificaciones@sistema.edu.ec',
        verbose_name='Correo remitente institucional'
    )
    maintenance_mode = models.BooleanField(
        default=False,
        verbose_name='Modo mantenimiento'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Última actualización'
    )
    updated_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Actualizado por'
    )

    class Meta:
        db_table = 'users_systemsetting'
        verbose_name = 'Parámetro del Sistema'
        verbose_name_plural = 'Parámetros del Sistema'

    def __str__(self):
        return "Configuración General de la Plataforma"

    @classmethod
    def get_settings(cls):
        """Retorna el objeto único de configuración del sistema o crea uno por defecto."""
        setting, _ = cls.objects.get_or_create(id=1)
        return setting


class SupportTicket(models.Model):
    """
    Modelo para tickets de soporte técnico e incidencias para el Administrador.
    """
    class Category(models.TextChoices):
        TECNICO = 'TECNICO', 'Problema Técnico / Error'
        CUENTA = 'CUENTA', 'Acceso y Cuenta'
        EVALUACIONES = 'EVALUACIONES', 'Dificultad con Evaluaciones'
        OTRO = 'OTRO', 'Otro / Consulta'

    class Priority(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'

    class Status(models.TextChoices):
        ABIERTO = 'ABIERTO', 'Abierto'
        EN_PROCESO = 'EN_PROCESO', 'En Proceso'
        RESUELTO = 'RESUELTO', 'Resuelto'
        CERRADO = 'CERRADO', 'Cerrado'

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='support_tickets',
        verbose_name='Usuario Solicitante'
    )
    subject = models.CharField(
        max_length=200,
        verbose_name='Asunto / Título'
    )
    description = models.TextField(
        verbose_name='Descripción de la incidencia'
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.TECNICO,
        verbose_name='Categoría'
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIA,
        verbose_name='Prioridad'
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.ABIERTO,
        verbose_name='Estado'
    )
    admin_response = models.TextField(
        blank=True,
        verbose_name='Respuesta Administrativa'
    )
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tickets',
        verbose_name='Atendido por'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de respuesta/actualización'
    )

    class Meta:
        db_table = 'users_supportticket'
        ordering = ['-created_at']
        verbose_name = 'Ticket de Soporte'
        verbose_name_plural = 'Tickets de Soporte'

    def __str__(self):
        return f"Ticket #{self.id} - {self.subject} ({self.get_status_display()})"



class TutorNote(models.Model):
    """
    Notas de seguimiento que el Tutor Académico deja en el perfil de un estudiante tutorado.
    """
    tutor = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='notes_written',
        verbose_name='Tutor'
    )
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='tutor_notes',
        verbose_name='Estudiante'
    )
    note = models.TextField(verbose_name='Nota de seguimiento')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha')

    class Meta:
        db_table = 'users_tutornote'
        ordering = ['-created_at']
        verbose_name = 'Nota de Tutor'
        verbose_name_plural = 'Notas de Tutor'

    def __str__(self):
        return f'Nota de {self.tutor.username} sobre {self.student.username}'

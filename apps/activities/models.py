from django.conf import settings
from django.db import models


class ActivityType(models.TextChoices):
    """Tipos de actividades formativas disponibles."""
    TALLER = 'TALLER', 'Taller'
    SEMINARIO = 'SEMINARIO', 'Seminario'
    DESAFIO = 'DESAFIO', 'Desafío'
    RETO_COLABORATIVO = 'RETO_COLABORATIVO', 'Reto Colaborativo'


class EnrollmentStatus(models.TextChoices):
    """Estados de inscripción a las actividades."""
    INSCRITO = 'INSCRITO', 'Inscrito'
    EN_CURSO = 'EN_CURSO', 'En Curso'
    COMPLETADO = 'COMPLETADO', 'Completado'
    CANCELADO = 'CANCELADO', 'Cancelado'


class Activity(models.Model):
    """
    Modelo que representa una Actividad Formativa en el sistema académico.
    """
    title = models.CharField(
        max_length=200,
        verbose_name='Título'
    )
    description = models.TextField(
        verbose_name='Descripción'
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        verbose_name='Tipo de Actividad'
    )
    competency = models.ForeignKey(
        'competencies.Competency',
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='Competencia'
    )
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activities_taught',
        verbose_name='Instructor'
    )

    max_participants = models.PositiveIntegerField(
        default=30,
        verbose_name='Máximo de Participantes'
    )
    start_date = models.DateTimeField(
        verbose_name='Fecha de Inicio'
    )
    end_date = models.DateTimeField(
        verbose_name='Fecha de Fin'
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Lugar o Enlace'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Está Activa'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Fecha de Actualización'
    )

    class Meta:
        db_table = 'activities_activity'
        verbose_name = 'Actividad'
        verbose_name_plural = 'Actividades'

    def __str__(self):
        return self.title


class Team(models.Model):
    """
    Modelo que representa un Equipo de trabajo dentro de una actividad formativa.
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre del Equipo'
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='teams',
        verbose_name='Actividad'
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='teams',
        blank=True,
        verbose_name='Miembros'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        db_table = 'activities_team'
        verbose_name = 'Equipo'
        verbose_name_plural = 'Equipos'

    def __str__(self):
        return f'{self.name} - {self.activity.title}'


class Enrollment(models.Model):
    """
    Modelo que representa la Inscripción de un estudiante a una actividad formativa.
    """
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Estudiante'
    )
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Actividad'
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollment_records',
        verbose_name='Equipo'
    )
    status = models.CharField(
        max_length=20,
        choices=EnrollmentStatus.choices,
        default=EnrollmentStatus.INSCRITO,
        verbose_name='Estado'
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Inscripción'
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Finalización'
    )

    class Meta:
        db_table = 'activities_enrollment'
        unique_together = [('student', 'activity')]
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'

    def __str__(self):
        return f'{self.student.get_full_name()} - {self.activity.title}'


class Challenge(models.Model):
    """
    Modelo que representa los detalles de un Desafío formativo asociado a una actividad.
    """
    activity = models.OneToOneField(
        Activity,
        on_delete=models.CASCADE,
        related_name='challenge_details',
        verbose_name='Actividad'
    )
    instructions = models.TextField(
        verbose_name='Instrucciones'
    )
    deliverable_description = models.TextField(
        verbose_name='Descripción del Entregable'
    )
    due_date = models.DateTimeField(
        verbose_name='Fecha de Entrega'
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=100,
        verbose_name='Puntuación Máxima'
    )

    class Meta:
        db_table = 'activities_challenge'
        verbose_name = 'Desafío'
        verbose_name_plural = 'Desafíos'

    def __str__(self):
        return f'Desafío: {self.activity.title}'

class MentorApplicationStatus(models.TextChoices):
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    APROBADO = 'APROBADO', 'Aprobado'
    RECHAZADO = 'RECHAZADO', 'Rechazado'

class MentorApplication(models.Model):
    """
    Modelo para la postulación de graduados como mentores en una actividad (HU12).
    """
    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name='mentor_applications',
        verbose_name='Actividad'
    )
    graduate = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentor_applications',
        verbose_name='Graduado'
    )
    status = models.CharField(
        max_length=20,
        choices=MentorApplicationStatus.choices,
        default=MentorApplicationStatus.PENDIENTE,
        verbose_name='Estado'
    )
    applied_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Solicitud'
    )

    class Meta:
        db_table = 'activities_mentorapplication'
        unique_together = [('graduate', 'activity')]
        verbose_name = 'Solicitud de Mentor'
        verbose_name_plural = 'Solicitudes de Mentores'

    def __str__(self):
        return f'{self.graduate.get_full_name()} - {self.activity.title} ({self.get_status_display()})'

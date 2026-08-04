from django.db import models


class Competency(models.Model):
    """
    Modelo que representa una Competencia Transversal.
    Ejemplos: Comunicación, Trabajo en equipo, Liderazgo.
    """
    name = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Nombre'
    )
    description = models.TextField(
        verbose_name='Descripción'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
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
        db_table = 'competencies_competency'
        verbose_name = 'Competencia'
        verbose_name_plural = 'Competencias'
        ordering = ['name']

    def __str__(self):
        return self.name


class Subcompetency(models.Model):
    """
    Modelo que representa una Subcompetencia asociada a una Competencia transversal.
    """
    competency = models.ForeignKey(
        Competency,
        on_delete=models.CASCADE,
        related_name='subcompetencies',
        verbose_name='Competencia'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )

    class Meta:
        db_table = 'competencies_subcompetency'
        verbose_name = 'Subcompetencia'
        verbose_name_plural = 'Subcompetencias'

    def __str__(self):
        return f'{self.competency.name} - {self.name}'


class Rubric(models.Model):
    """
    Modelo que representa una Rúbrica con niveles de dominio para una Subcompetencia.
    """
    class Level(models.TextChoices):
        INICIAL = 'INICIAL', 'Inicial'
        EN_DESARROLLO = 'EN_DESARROLLO', 'En Desarrollo'
        COMPETENTE = 'COMPETENTE', 'Competente'
        EXCELENTE = 'EXCELENTE', 'Excelente'

    subcompetency = models.ForeignKey(
        Subcompetency,
        on_delete=models.CASCADE,
        related_name='rubrics',
        verbose_name='Subcompetencia'
    )
    level = models.CharField(
        max_length=20,
        choices=Level.choices,
        verbose_name='Nivel de dominio'
    )
    description = models.TextField(
        verbose_name='Descripción del nivel'
    )
    min_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Puntaje mínimo'
    )
    max_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Puntaje máximo'
    )

    class Meta:
        db_table = 'competencies_rubric'
        verbose_name = 'Rúbrica'
        verbose_name_plural = 'Rúbricas'
        unique_together = [('subcompetency', 'level')]

    def __str__(self):
        return f'{self.subcompetency.name} - {self.get_level_display()}'

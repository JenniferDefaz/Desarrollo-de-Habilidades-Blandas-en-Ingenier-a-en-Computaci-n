from django.db import migrations


def populate_roles(apps, schema_editor):
    Role = apps.get_model('users', 'Role')
    roles_data = [
        ('ESTUDIANTE', 'Estudiante'),
        ('DOCENTE', 'Docente'),
        ('TUTOR_ACADEMICO', 'Tutor Académico'),
        ('COORDINADOR_CARRERA', 'Coordinador de Carrera'),
        ('EMPRESA_COLABORADORA', 'Empresa Colaboradora'),
        ('GRADUADO', 'Graduado'),
        ('BIENESTAR_UNIVERSITARIO', 'Bienestar Universitario'),
        ('ADMINISTRADOR', 'Administrador'),
    ]
    for code, _ in roles_data:
        Role.objects.get_or_create(name=code)


def reverse_roles(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_roles, reverse_roles),
    ]

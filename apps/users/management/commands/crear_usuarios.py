from django.core.management.base import BaseCommand
from apps.users.models import CustomUser, Role, UserProfile


USUARIOS = [
    {
        'username': 'Robinson',
        'password': '@Vinicio2004',
        'first_name': 'Robinson',
        'last_name': '',
        'role': Role.RoleChoices.ESTUDIANTE,
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'Vinicio',
        'password': '0504652140',
        'first_name': 'Vinicio',
        'last_name': '',
        'role': Role.RoleChoices.ADMINISTRADOR,
        'is_staff': True,
        'is_superuser': True,
    },
    {
        'username': 'Juan',
        'password': '1234567890',
        'first_name': 'Juan',
        'last_name': '',
        'role': Role.RoleChoices.DOCENTE,
        'is_staff': False,
        'is_superuser': False,
    },
    {
        'username': 'coordinador',
        'password': 'coordinador',
        'first_name': 'Coordinador',
        'last_name': '',
        'role': Role.RoleChoices.COORDINADOR_CARRERA,
        'is_staff': False,
        'is_superuser': False,
    },
]


class Command(BaseCommand):
    help = 'Crea los usuarios iniciales del sistema con sus roles'

    def handle(self, *args, **options):
        self.stdout.write('Creando roles...')

        # Crear todos los roles si no existen
        for role_choice in Role.RoleChoices:
            role, created = Role.objects.get_or_create(name=role_choice.value)
            if created:
                self.stdout.write(f'  Rol creado: {role_choice.value}')

        self.stdout.write('Creando usuarios...')

        for data in USUARIOS:
            username = data['username']

            if CustomUser.objects.filter(username=username).exists():
                self.stdout.write(
                    self.style.WARNING(f'  Usuario "{username}" ya existe, se omite.')
                )
                continue

            role = Role.objects.get(name=data['role'])

            user = CustomUser.objects.create_user(
                username=username,
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                role=role,
                is_staff=data['is_staff'],
                is_superuser=data['is_superuser'],
                is_active=True,
            )

            # Crear perfil asociado si no existe
            UserProfile.objects.get_or_create(user=user)

            self.stdout.write(
                self.style.SUCCESS(
                    f'  Usuario creado: {username} | Rol: {role.name}'
                )
            )

        self.stdout.write(self.style.SUCCESS('\nUsuarios creados exitosamente.'))

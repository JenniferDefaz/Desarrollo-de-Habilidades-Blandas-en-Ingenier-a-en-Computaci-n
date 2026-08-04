from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Role, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline para mostrar el perfil dentro del formulario de usuario."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'
    fk_name = 'user'


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [UserProfileInline]
    list_display = ('username', 'first_name', 'last_name', 'institutional_email', 'role', 'is_active')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'cedula', 'institutional_email')
    fieldsets = UserAdmin.fieldsets + (
        ('Información Institucional', {
            'fields': ('cedula', 'role', 'phone', 'institutional_email'),
        }),
    )

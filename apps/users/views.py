from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from core.decorators import role_required
from django.contrib import messages
from .models import CustomUser, Role
from .forms import UserCreateForm, UserUpdateForm



def ensure_default_roles():
    """Asegura que existan los roles por defecto en la base de datos."""
    if not Role.objects.exists():
        for role_code, _ in Role.RoleChoices.choices:
            Role.objects.get_or_create(name=role_code)


@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def user_list(request):
    """Lista todos los usuarios con sus roles."""
    users = CustomUser.objects.select_related('role').all().order_by('-date_joined')
    return render(request, 'users/user_list.html', {'users': users})


@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def user_create(request):
    """Crea un nuevo usuario."""
    from apps.evaluations.utils import log_action
    ensure_default_roles()
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            log_action(
                user=request.user,
                action='CREAR_USUARIO',
                model_name='CustomUser',
                object_id=new_user.id,
                changes={'username': new_user.username, 'role': new_user.role.name if new_user.role else 'Sin Rol'},
                request=request
            )
            messages.success(request, 'Usuario creado exitosamente.')
            return redirect('user_list')
    else:
        form = UserCreateForm()
    roles = Role.objects.all()
    return render(request, 'users/user_form.html', {
        'form': form,
        'roles': roles,
        'user_obj': None,
    })


@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def user_update(request, pk):
    """Edita un usuario existente."""
    from apps.evaluations.utils import log_action
    ensure_default_roles()
    user_obj = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=user_obj)
        if form.is_valid():
            updated_user = form.save()
            log_action(
                user=request.user,
                action='EDITAR_USUARIO',
                model_name='CustomUser',
                object_id=updated_user.id,
                changes={'username': updated_user.username, 'role': updated_user.role.name if updated_user.role else 'Sin Rol'},
                request=request
            )
            messages.success(request, 'Usuario actualizado exitosamente.')
            return redirect('user_list')
    else:
        form = UserUpdateForm(instance=user_obj)
    roles = Role.objects.all()
    return render(request, 'users/user_form.html', {
        'form': form,
        'roles': roles,
        'user_obj': user_obj,
    })


@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def user_delete(request, pk):
    """Elimina un usuario (POST only)."""
    from apps.evaluations.utils import log_action
    user_obj = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        name = user_obj.get_full_name()
        uid = user_obj.id
        uname = user_obj.username
        user_obj.delete()
        log_action(
            user=request.user,
            action='ELIMINAR_USUARIO',
            model_name='CustomUser',
            object_id=uid,
            changes={'username': uname, 'name': name},
            request=request
        )
        messages.success(request, f'Usuario "{name}" eliminado exitosamente.')
    return redirect('user_list')



# --- VISTAS DE PERFIL Y CONFIGURACIÓN ---

@login_required
def profile_view(request):
    """Vista para consultar y actualizar el perfil del usuario autenticado."""
    from .forms import ProfileEditForm
    user = request.user
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente.')
            return redirect('user_profile')
    else:
        form = ProfileEditForm(instance=user)

    return render(request, 'users/profile.html', {
        'form': form,
        'user_obj': user
    })


@login_required
def settings_view(request):
    """Vista de configuración y cambio de contraseña para el usuario."""
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm

    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return render(request, 'users/settings.html', {
            'form': form
        })
    return render(request, 'users/settings.html', {
        'form': PasswordChangeForm(user=request.user)
    })


@role_required(['ADMINISTRADOR'])
def system_settings_view(request):
    """Vista para gestionar la configuración de parámetros generales de la plataforma (RF23)."""
    from apps.evaluations.utils import log_action
    from .models import SystemSetting
    from .forms import SystemSettingForm

    settings_obj = SystemSetting.get_settings()

    if request.method == 'POST':
        form = SystemSettingForm(request.POST, instance=settings_obj)
        if form.is_valid():
            updated_setting = form.save(commit=False)
            updated_setting.updated_by = request.user
            updated_setting.save()

            log_action(
                user=request.user,
                action='ACTUALIZAR_PARAMETROS_SISTEMA',
                model_name='SystemSetting',
                object_id=updated_setting.id,
                changes={
                    'max_file_size_mb': updated_setting.max_file_size_mb,
                    'maintenance_mode': updated_setting.maintenance_mode
                },
                request=request
            )
            messages.success(request, 'Parámetros generales de la plataforma actualizados exitosamente.')
            return redirect('system_settings_view')
    else:
        form = SystemSettingForm(instance=settings_obj)

    return render(request, 'users/system_settings.html', {
        'form': form,
        'settings_obj': settings_obj
    })


@login_required
def support_ticket_list(request):
    """Bandeja de tickets de soporte técnico e incidencias (RF23)."""
    from .models import SupportTicket

    is_admin = request.user.role and request.user.role.name in ['ADMINISTRADOR', 'COORDINADOR_CARRERA']

    if is_admin:
        tickets = SupportTicket.objects.select_related('user', 'assigned_to').all()
    else:
        tickets = SupportTicket.objects.filter(user=request.user)

    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')

    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if category_filter:
        tickets = tickets.filter(category=category_filter)

    return render(request, 'users/support_ticket_list.html', {
        'tickets': tickets,
        'is_admin': is_admin,
        'status_filter': status_filter,
        'category_filter': category_filter
    })


@login_required
def support_ticket_create(request):
    """Formulario para que cualquier usuario cree un ticket de soporte técnico (RF23)."""
    from apps.evaluations.utils import log_action
    from .forms import SupportTicketForm

    if request.method == 'POST':
        form = SupportTicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            log_action(
                user=request.user,
                action='CREAR_TICKET_SOPORTE',
                model_name='SupportTicket',
                object_id=ticket.id,
                changes={'subject': ticket.subject, 'category': ticket.category},
                request=request
            )

            messages.success(request, f'Ticket de soporte #{ticket.id} creado exitosamente. Un administrador atenderá tu consulta a la brevedad.')
            return redirect('support_ticket_list')
    else:
        form = SupportTicketForm()

    return render(request, 'users/support_ticket_form.html', {
        'form': form
    })


@login_required
def support_ticket_detail(request, pk):
    """Detalle del ticket y respuesta administrativa (RF23)."""
    from apps.evaluations.utils import log_action
    from apps.notifications.models import Notification, NotificationType
    from .models import SupportTicket

    is_admin = request.user.role and request.user.role.name in ['ADMINISTRADOR', 'COORDINADOR_CARRERA']

    if is_admin:
        ticket = get_object_or_404(SupportTicket, pk=pk)
    else:
        ticket = get_object_or_404(SupportTicket, pk=pk, user=request.user)

    if request.method == 'POST' and is_admin:
        response_text = request.POST.get('admin_response', '')
        new_status = request.POST.get('status', ticket.status)

        ticket.admin_response = response_text
        ticket.status = new_status
        ticket.assigned_to = request.user
        ticket.save()

        Notification.objects.create(
            recipient=ticket.user,
            title=f'Respuesta a Ticket #{ticket.id}',
            message=f'Tu ticket "{ticket.subject}" ha sido actualizado a estado: {ticket.get_status_display()}',
            notification_type=NotificationType.SISTEMA,
            link=f'/usuarios/soporte/{ticket.id}/'
        )

        log_action(
            user=request.user,
            action='RESPONDER_TICKET_SOPORTE',
            model_name='SupportTicket',
            object_id=ticket.id,
            changes={'status': new_status, 'response': response_text[:50]},
            request=request
        )

        messages.success(request, 'Respuesta registrada y usuario notificado exitosamente.')
        return redirect('support_ticket_detail', pk=ticket.id)

    return render(request, 'users/support_ticket_detail.html', {
        'ticket': ticket,
        'is_admin': is_admin
    })

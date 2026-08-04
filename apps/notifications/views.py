from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification


@login_required
def notification_list(request):
    """Lista de notificaciones in-app para el usuario autenticado."""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })


@login_required
def mark_as_read(request, pk):
    """Marcar una notificación como leída y redirigir al link adjunto si existe."""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=['is_read'])
    
    if notification.link:
        return redirect(notification.link)
    return redirect('notification_list')


@login_required
def mark_all_as_read(request):
    """Marcar todas las notificaciones del usuario como leídas."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    messages.success(request, 'Todas las notificaciones han sido marcadas como leídas.')
    return redirect('notification_list')

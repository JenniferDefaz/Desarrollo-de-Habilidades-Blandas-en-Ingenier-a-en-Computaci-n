from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles):
    """
    Decorator for views that checks that the user is logged in and has a specific role,
    redirecting to the dashboard with an error or raising a 403 Forbidden.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if hasattr(request.user, 'role') and request.user.role and request.user.role.name in allowed_roles:
                return view_func(request, *args, **kwargs)
                
            messages.error(request, 'No tienes permiso para acceder a esta página.')
            return redirect('dashboard')
            
        return _wrapped_view
    return decorator

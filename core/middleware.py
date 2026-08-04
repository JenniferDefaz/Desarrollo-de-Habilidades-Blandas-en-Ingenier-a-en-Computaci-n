from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from django.utils.cache import add_never_cache_headers


class DisableCacheMiddleware:
    """
    Middleware que deshabilita el almacenamiento en caché del navegador (bfcache y caché de disco)
    para respuestas autenticadas y páginas de inicio/cierre de sesión.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        add_never_cache_headers(response)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response


class SingleSessionMiddleware:
    """
    Middleware que garantiza que solo exista una única sesión activa por usuario.
    Si el usuario inicia sesión en otro navegador o dispositivo, invalida la sesión previa
    y notifica al usuario el motivo del cierre de sesión.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_session_key = getattr(request.user, 'session_key', None)
            current_session_key = request.session.session_key
            
            # Si el usuario ya tiene una clave de sesión diferente registrada
            if user_session_key and current_session_key and user_session_key != current_session_key:
                from django.contrib.sessions.models import Session
                from django.http import JsonResponse

                messages.warning(
                    request, 
                    'Tu sesión se ha cerrado automáticamente porque se ha iniciado sesión con tu cuenta desde otro navegador o dispositivo.'
                )
                old_key = current_session_key
                logout(request)
                Session.objects.filter(session_key=old_key).delete()

                is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.path == '/api/check-session/'
                if is_ajax:
                    return JsonResponse({
                        'session_valid': False,
                        'redirect_url': '/login/'
                    })

                return redirect('login')

        response = self.get_response(request)
        return response

class SecurityHeadersMiddleware:
    """
    Middleware que añade cabeceras de seguridad adicionales a cada respuesta HTTP.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Restringir acceso a funcionalidades del dispositivo
        response['Permissions-Policy'] = "camera=(), microphone=(), geolocation=()"
        
        # Política de seguridad de contenido (básica)
        # Permite scripts de dominios de confianza usados en el sistema
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://code.jquery.com https://cdn.jsdelivr.net https://cdn.datatables.net https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdn.datatables.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com;"
        )
        response['Content-Security-Policy'] = csp
        
        return response

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.users.models import CustomUser
from apps.competencies.models import Competency
from apps.evaluations.models import Evaluation360
from apps.activities.models import Activity
from core.decorators import role_required


from django.views.decorators.cache import never_cache
from django.contrib.sessions.models import Session


from django.middleware.csrf import get_token, rotate_token
from django.http import JsonResponse


def home(request):
    """Página de inicio pública (landing page)."""
    return render(request, 'core/home.html')


def csrf_failure(request, reason=""):
    """Manejador personalizado para errores CSRF (evita la pantalla amarilla 403)."""
    messages.warning(request, 'El token de seguridad o la sesión del formulario ha caducado. Por favor, vuelva a ingresar sus credenciales.')
    return redirect('login')


def check_session_status(request):
    """Verifica si la sesión del usuario sigue siendo válida."""
    if not request.user.is_authenticated:
        return JsonResponse({'session_valid': False, 'redirect_url': '/login/'})
    return JsonResponse({'session_valid': True})


@never_cache
def login_view(request):
    """Vista de inicio de sesión personalizada con protección contra fuerza bruta."""
    get_token(request)
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Check rate limiting
    failed_attempts = request.session.get('failed_login_attempts', 0)
    lockout_time = request.session.get('login_lockout_time', 0)
    import time
    
    if lockout_time and time.time() < lockout_time:
        remaining_time = int((lockout_time - time.time()) / 60)
        messages.error(request, f'Demasiados intentos fallidos. Intente de nuevo en {remaining_time} minutos.')
        return render(request, 'core/login.html')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Reset rate limit on success
            request.session['failed_login_attempts'] = 0
            request.session['login_lockout_time'] = 0
            
            login(request, user)
            if remember_me:
                request.session.set_expiry(1209600)  # 2 semanas (14 días)
            else:
                request.session.set_expiry(0)  # Expira al cerrar el navegador

            user.session_key = request.session.session_key
            user.save(update_fields=['session_key'])

            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
                
            if hasattr(user, 'role') and user.role:
                if user.role.name == 'ESTUDIANTE':
                    return redirect('student_dashboard')
                elif user.role.name == 'DOCENTE':
                    return redirect('teacher_dashboard')
                elif user.role.name in ['COORDINADOR_CARRERA', 'ADMINISTRADOR']:
                    return redirect('coordinator_dashboard')
                elif user.role.name == 'GRADUADO':
                    return redirect('graduate_dashboard')
            return redirect('dashboard')
        else:
            failed_attempts += 1
            request.session['failed_login_attempts'] = failed_attempts
            
            if failed_attempts >= 5:
                # Lock out for 5 minutes
                request.session['login_lockout_time'] = time.time() + 300
                messages.error(request, 'Demasiados intentos fallidos. Su cuenta ha sido bloqueada temporalmente por seguridad. Intente en 5 minutos.')
            else:
                remaining = 5 - failed_attempts
                messages.error(request, f'Usuario o contraseña incorrectos. Intentos restantes: {remaining}.')
                
    return render(request, 'core/login.html')


@never_cache
def logout_view(request):
    """Cierra la sesión del usuario."""
    if request.user.is_authenticated:
        request.user.session_key = None
        request.user.save(update_fields=['session_key'])
    logout(request)
    rotate_token(request)
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('login')


@login_required
def dashboard(request):
    """Router dashboard depending on user role."""
    user = request.user
    if user.is_superuser:
        return redirect('coordinator_dashboard')

    if hasattr(user, 'role') and user.role:
        if user.role.name == 'ESTUDIANTE':
            return redirect('student_dashboard')
        elif user.role.name == 'DOCENTE':
            return redirect('teacher_dashboard')
        elif user.role.name in ['COORDINADOR_CARRERA', 'ADMINISTRADOR']:
            return redirect('coordinator_dashboard')
        elif user.role.name == 'GRADUADO':
            return redirect('graduate_dashboard')
    
    return render(request, 'core/dashboard_home.html')



@login_required
@role_required(['ESTUDIANTE'])
def student_dashboard(request):
    from apps.evaluations.models import Evaluation360, EvaluationScore
    from apps.activities.models import Enrollment, EnrollmentStatus

    diag_eval = Evaluation360.objects.filter(
        evaluated=request.user,
        evaluation_type=Evaluation360.EvaluationType.AUTOEVALUACION,
        period='DIAGNOSTICO_INICIAL',
        status=Evaluation360.Status.COMPLETADA
    ).first()

    scores = []
    if diag_eval:
        scores = EvaluationScore.objects.filter(evaluation=diag_eval).select_related('subcompetency__competency')

    my_enrollments = Enrollment.objects.filter(
        student=request.user,
        status=EnrollmentStatus.INSCRITO
    ).select_related('activity')

    context = {
        'diag_completed': bool(diag_eval),
        'scores': scores,
        'my_enrollments': my_enrollments
    }
    return render(request, 'core/student_dashboard.html', context)


@login_required
@role_required(['DOCENTE'])
def teacher_dashboard(request):
    return render(request, 'core/teacher_dashboard.html')


@login_required
@role_required(['GRADUADO'])
def graduate_dashboard(request):
    """Panel principal para el rol Graduado."""
    from apps.activities.models import MentorApplication
    from apps.evaluations.models import GraduateFeedback

    my_applications = MentorApplication.objects.filter(
        graduate=request.user
    ).select_related('activity').order_by('-applied_at')

    my_feedbacks = GraduateFeedback.objects.filter(
        graduate=request.user
    ).select_related('competency').order_by('-created_at')

    pending_count = my_applications.filter(status='PENDIENTE').count()
    approved_count = my_applications.filter(status='APROBADO').count()

    return render(request, 'core/graduate_dashboard.html', {
        'my_applications': my_applications[:5],
        'my_feedbacks': my_feedbacks[:5],
        'pending_count': pending_count,
        'approved_count': approved_count,
        'total_feedbacks': my_feedbacks.count(),
    })


@login_required
@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def coordinator_dashboard(request):
    """Panel de control para coordinador/admin."""
    context = {
        'total_users': CustomUser.objects.count(),
        'total_competencies': Competency.objects.count(),
        'total_evaluations': Evaluation360.objects.count(),
        'total_activities': Activity.objects.count(),
        'recent_users': CustomUser.objects.select_related('role').order_by('-date_joined')[:5],
    }
    return render(request, 'core/coordinator_dashboard.html', context)

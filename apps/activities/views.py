from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from core.decorators import role_required
from .models import Activity, Enrollment, EnrollmentStatus
from .forms import ActivityForm

# --- VISTAS PARA DOCENTES Y COORDINADORES ---

@role_required(['DOCENTE', 'COORDINADOR_CARRERA', 'ADMINISTRADOR', 'BIENESTAR_UNIVERSITARIO'])
def activity_list(request):
    """Lista de actividades formativas para gestión docente."""
    user_role = request.user.role.name if request.user.role else ''
    if user_role in ['DOCENTE', 'Docente']:
        activities = Activity.objects.filter(
            Q(instructor=request.user) | Q(instructor__isnull=True)
        ).annotate(
            enrolled_count=Count('enrollments', filter=Q(enrollments__status=EnrollmentStatus.INSCRITO))
        ).order_by('-created_at')
    else:
        activities = Activity.objects.all().annotate(
            enrolled_count=Count('enrollments', filter=Q(enrollments__status=EnrollmentStatus.INSCRITO))
        ).order_by('-created_at')
    return render(request, 'activities/activity_list.html', {'activities': activities})

@role_required(['DOCENTE', 'COORDINADOR_CARRERA', 'ADMINISTRADOR', 'BIENESTAR_UNIVERSITARIO'])
def activity_create(request):
    """Crear una nueva actividad formativa."""
    if request.method == 'POST':
        form = ActivityForm(request.POST)
        if form.is_valid():
            activity = form.save(commit=False)
            if not activity.instructor:
                activity.instructor = request.user
            activity.save()
            messages.success(request, f'Actividad formativa "{activity.title}" creada exitosamente.')
            return redirect('activity_list')
        else:
            messages.error(request, 'No se pudo guardar la actividad. Por favor verifica que todos los campos requeridos estén completos.')
    else:
        form = ActivityForm(initial={'instructor': request.user})
    return render(request, 'activities/activity_form.html', {'form': form, 'obj': None})


@role_required(['DOCENTE', 'COORDINADOR_CARRERA', 'ADMINISTRADOR', 'BIENESTAR_UNIVERSITARIO'])
def activity_update(request, pk):
    """Editar una actividad formativa existente."""
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == 'POST':
        form = ActivityForm(request.POST, instance=activity)
        if form.is_valid():
            form.save()
            messages.success(request, 'Actividad formativa actualizada exitosamente.')
            return redirect('activity_list')
    else:
        form = ActivityForm(instance=activity)
    return render(request, 'activities/activity_form.html', {'form': form, 'obj': activity})

@role_required(['DOCENTE', 'COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def activity_delete(request, pk):
    """Eliminar una actividad formativa."""
    activity = get_object_or_404(Activity, pk=pk)
    if request.method == 'POST':
        activity.delete()
        messages.success(request, 'Actividad eliminada correctamente.')
    return redirect('activity_list')

@role_required(['DOCENTE', 'COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def activity_detail(request, pk):
    """Detalle de una actividad e inscritos."""
    activity = get_object_or_404(Activity, pk=pk)
    enrollments = activity.enrollments.select_related('student').all()
    return render(request, 'activities/activity_detail.html', {
        'activity': activity,
        'enrollments': enrollments
    })


# --- VISTAS PARA ESTUDIANTES ---

@role_required(['ESTUDIANTE', 'GRADUADO'])
def student_activities(request):
    """Catálogo de actividades disponibles e inscripciones del estudiante."""
    user_enrollments = Enrollment.objects.filter(student=request.user).values_list('activity_id', flat=True)
    
    activities = Activity.objects.filter(is_active=True).annotate(
        enrolled_count=Count('enrollments', filter=Q(enrollments__status=EnrollmentStatus.INSCRITO))
    ).prefetch_related('teams__members').order_by('-start_date')
    
    my_enrollments = Enrollment.objects.filter(student=request.user).select_related('activity')
    
    return render(request, 'activities/student_activities.html', {
        'activities': activities,
        'user_enrolled_ids': list(user_enrollments),
        'my_enrollments': my_enrollments
    })

@role_required(['ESTUDIANTE'])
def enroll_activity(request, pk):
    """Inscribirse a una actividad formativa."""
    activity = get_object_or_404(Activity, pk=pk, is_active=True)
    current_count = activity.enrollments.filter(status=EnrollmentStatus.INSCRITO).count()
    
    if current_count >= activity.max_participants:
        messages.error(request, 'La actividad ya no cuenta con cupos disponibles.')
        return redirect('student_activities')
        
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        activity=activity,
        defaults={'status': EnrollmentStatus.INSCRITO}
    )
    
    if not created:
        if enrollment.status == EnrollmentStatus.CANCELADO:
            enrollment.status = EnrollmentStatus.INSCRITO
            enrollment.save()
            messages.success(request, f'Te has vuelto a inscribir en {activity.title}.')
        else:
            messages.info(request, 'Ya estás inscrito en esta actividad.')
    else:
        messages.success(request, f'¡Inscripción exitosa en {activity.title}!')
        
    return redirect('student_activities')

@role_required(['ESTUDIANTE'])
def cancel_enrollment(request, pk):
    """Cancelar inscripción a una actividad."""
    activity = get_object_or_404(Activity, pk=pk)
    enrollment = Enrollment.objects.filter(student=request.user, activity=activity).first()
    
    if enrollment:
        enrollment.status = EnrollmentStatus.CANCELADO
        enrollment.save()
        messages.success(request, 'Has cancelado tu inscripción.')
    else:
        messages.error(request, 'No te encuentras inscrito en esta actividad.')
        
    return redirect('student_activities')


# --- RETOS COLABORATIVOS Y EQUIPOS ---

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'DOCENTE'])
def challenges_list(request):
    """Gestión de retos colaborativos por el Coordinador/Docente."""
    from .models import ActivityType, Team
    challenges = Activity.objects.filter(activity_type=ActivityType.RETO_COLABORATIVO).prefetch_related('teams')
    return render(request, 'activities/challenges_list.html', {'challenges': challenges})

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'DOCENTE'])
def manage_teams(request, activity_id):
    """Gestionar equipos y participantes para un reto colaborativo."""
    from apps.users.models import CustomUser
    from .models import Team
    activity = get_object_or_404(Activity, pk=activity_id)
    teams = activity.teams.prefetch_related('members').all()
    students = CustomUser.objects.filter(role__name='ESTUDIANTE', is_active=True)

    if request.method == 'POST':
        team_name = request.POST.get('team_name')
        selected_members = request.POST.getlist('members')
        if team_name:
            team = Team.objects.create(name=team_name, activity=activity)
            if selected_members:
                team.members.set(selected_members)
                # Auto-inscribir a los estudiantes en la actividad si no lo estaban
                for student_id in selected_members:
                    Enrollment.objects.get_or_create(
                        activity=activity,
                        student_id=student_id,
                        defaults={'status': EnrollmentStatus.INSCRITO}
                    )
            messages.success(request, f'Equipo "{team_name}" creado exitosamente.')
            return redirect('manage_teams', activity_id=activity.id)

    return render(request, 'activities/manage_teams.html', {
        'activity': activity,
        'teams': teams,
        'students': students
    })

# --- GESTIÓN DE MENTORES ---

@role_required(['GRADUADO'])
def apply_as_mentor(request, pk):
    """Permitir a un graduado postularse como mentor para una actividad."""
    from .models import MentorApplication, MentorApplicationStatus
    activity = get_object_or_404(Activity, pk=pk, is_active=True)
    
    app, created = MentorApplication.objects.get_or_create(
        activity=activity,
        graduate=request.user,
        defaults={'status': MentorApplicationStatus.PENDIENTE}
    )
    if created:
        messages.success(request, 'Tu solicitud para ser mentor ha sido enviada exitosamente.')
    else:
        messages.info(request, f'Ya tienes una solicitud en estado: {app.get_status_display()}')
    
    return redirect('student_activities')  # O donde listemos las actividades para ellos

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def manage_mentors(request, activity_id):
    """Permitir al Coordinador de Carrera aprobar o rechazar mentores."""
    from .models import MentorApplication, MentorApplicationStatus
    from django.core.mail import EmailMessage
    from django.conf import settings
    from django.template.loader import get_template
    from django.utils import timezone
    from io import BytesIO

    activity = get_object_or_404(Activity, pk=activity_id)
    applications = activity.mentor_applications.select_related('graduate').all()

    if request.method == 'POST':
        app_id = request.POST.get('application_id')
        action = request.POST.get('action')
        if app_id and action in ['APROBAR', 'RECHAZAR']:
            application = get_object_or_404(MentorApplication, id=app_id, activity=activity)
            graduate = application.graduate
            graduate_email = graduate.institutional_email or graduate.email
            approved = action == 'APROBAR'

            if approved:
                application.status = MentorApplicationStatus.APROBADO
                messages.success(request, f'Solicitud de {graduate.get_full_name()} aprobada.')
            else:
                application.status = MentorApplicationStatus.RECHAZADO
                messages.warning(request, f'Solicitud de {graduate.get_full_name()} rechazada.')

            application.save()

            # Generar PDF y enviar correo
            if graduate_email:
                try:
                    pdf_context = {
                        'approved': approved,
                        'graduate_name': graduate.get_full_name() or graduate.username,
                        'graduate_username': graduate.username,
                        'graduate_email': graduate_email,
                        'activity_title': activity.title,
                        'activity_type': activity.get_activity_type_display(),
                        'activity_date': activity.start_date.strftime('%d/%m/%Y %H:%M'),
                        'activity_location': activity.location,
                        'activity_competency': activity.competency.name if activity.competency else 'N/A',
                        'coordinator_name': request.user.get_full_name() or request.user.username,
                        'resolution_date': timezone.now().strftime('%d/%m/%Y %H:%M'),
                    }

                    # Generar PDF con xhtml2pdf
                    pdf_data = None
                    try:
                        from xhtml2pdf import pisa
                        template = get_template('activities/pdf/mentor_approval.html')
                        html = template.render(pdf_context)
                        pdf_buffer = BytesIO()
                        pisa.pisaDocument(BytesIO(html.encode('UTF-8')), pdf_buffer, encoding='UTF-8')
                        pdf_data = pdf_buffer.getvalue()
                    except Exception:
                        pdf_data = None

                    if approved:
                        subject = 'Postulacion como Mentor APROBADA - ' + activity.title
                        body = (
                            'Estimado/a ' + (graduate.first_name or graduate.username) + ',\n\n'
                            'Tu postulacion como Mentor en "' + activity.title + '" ha sido APROBADA.\n'
                            'Adjuntamos el documento oficial con los detalles.\n\n'
                            'Gracias por tu aporte a la formacion academica!\n\n'
                            'Saludos,\nSistema Academico - Habilidades Blandas'
                        )
                    else:
                        subject = 'Resultado de tu postulacion como Mentor - ' + activity.title
                        body = (
                            'Estimado/a ' + (graduate.first_name or graduate.username) + ',\n\n'
                            'Tu postulacion como Mentor en "' + activity.title + '" no fue aprobada.\n'
                            'Adjuntamos el documento con los detalles de la resolucion.\n\n'
                            'Te invitamos a postularte en otras actividades.\n\n'
                            'Saludos,\nSistema Academico - Habilidades Blandas'
                        )

                    email = EmailMessage(
                        subject=subject,
                        body=body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[graduate_email],
                    )

                    if pdf_data:
                        estado = 'aprobacion' if approved else 'resultado'
                        email.attach(
                            f'postulacion_mentor_{estado}.pdf',
                            pdf_data,
                            'application/pdf'
                        )

                    email.send(fail_silently=False)

                except Exception as e:
                    import logging
                    logging.getLogger(__name__).error(f'Error enviando correo a mentor: {e}')

            return redirect('manage_mentors', activity_id=activity.id)

    return render(request, 'activities/manage_mentors.html', {
        'activity': activity,
        'applications': applications
    })


@role_required(['GRADUADO'])
def my_mentor_applications(request):
    """Lista de postulaciones de mentoría del graduado con su estado actual."""
    from .models import MentorApplication
    applications = MentorApplication.objects.filter(
        graduate=request.user
    ).select_related('activity').order_by('-applied_at')

    return render(request, 'activities/my_mentor_applications.html', {
        'applications': applications
    })



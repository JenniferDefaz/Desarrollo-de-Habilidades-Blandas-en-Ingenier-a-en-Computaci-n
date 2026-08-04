from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from core.decorators import role_required
from apps.users.models import CustomUser
from apps.competencies.models import Competency, Subcompetency, Rubric
from apps.activities.models import Team, Activity, Enrollment, EnrollmentStatus
from .models import Evaluation360, EvaluationScore

# --- DIAGNÓSTICO INICIAL (HU03) ---

@role_required(['ESTUDIANTE'])
def initial_diagnostic(request):
    """Formulario interactivo para que el estudiante complete su diagnóstico inicial (HU03)."""
    existing_diag = Evaluation360.objects.filter(
        evaluated=request.user,
        evaluation_type=Evaluation360.EvaluationType.AUTOEVALUACION,
        period='DIAGNOSTICO_INICIAL'
    ).first()

    if existing_diag and existing_diag.status == Evaluation360.Status.COMPLETADA:
        messages.info(request, 'Ya has completado tu Diagnóstico Inicial de Habilidades Blandas.')
        return redirect('student_dashboard')

    competencies = Competency.objects.filter(is_active=True).prefetch_related('subcompetencies__rubrics')

    if request.method == 'POST':
        evaluation = existing_diag or Evaluation360.objects.create(
            title='Diagnóstico Inicial de Entrada',
            description='Evaluación inicial de autopercepción de competencias transversales.',
            competency=competencies.first(),
            evaluator=request.user,
            evaluated=request.user,
            evaluation_type=Evaluation360.EvaluationType.AUTOEVALUACION,
            period='DIAGNOSTICO_INICIAL',
            status=Evaluation360.Status.EN_PROGRESO
        )

        for comp in competencies:
            for sub in comp.subcompetencies.filter(is_active=True):
                score_val = request.POST.get(f'subcompetency_{sub.id}')
                if score_val:
                    try:
                        score_num = float(score_val)
                        EvaluationScore.objects.update_or_create(
                            evaluation=evaluation,
                            subcompetency=sub,
                            defaults={'score': score_num}
                        )
                    except ValueError:
                        pass

        evaluation.status = Evaluation360.Status.COMPLETADA
        evaluation.completed_at = timezone.now()
        evaluation.save()

        messages.success(request, '¡Felicidades! Has completado tu Diagnóstico Inicial exitosamente.')
        return redirect('student_dashboard')

    return render(request, 'evaluations/diagnostic_form.html', {
        'competencies': competencies
    })

@role_required(['ESTUDIANTE'])
def self_evaluation(request):
    """Formulario interactivo para autoevaluación periódica (HU04)."""
    competencies = Competency.objects.filter(is_active=True).prefetch_related('subcompetencies__rubrics')

    if request.method == 'POST':
        evaluation = Evaluation360.objects.create(
            title='Autoevaluación de Habilidades Blandas',
            description='Autoevaluación periódica de desarrollo de competencias transversales.',
            competency=competencies.first(),
            evaluator=request.user,
            evaluated=request.user,
            evaluation_type=Evaluation360.EvaluationType.AUTOEVALUACION,
            period='PERIODO_REGULAR',
            status=Evaluation360.Status.EN_PROGRESO
        )

        for comp in competencies:
            for sub in comp.subcompetencies.filter(is_active=True):
                score_val = request.POST.get(f'subcompetency_{sub.id}')
                if score_val:
                    try:
                        score_num = float(score_val)
                        EvaluationScore.objects.create(
                            evaluation=evaluation,
                            subcompetency=sub,
                            score=score_num
                        )
                    except ValueError:
                        pass

        evaluation.status = Evaluation360.Status.COMPLETADA
        evaluation.completed_at = timezone.now()
        evaluation.save()

        messages.success(request, 'Has registrado tu autoevaluación exitosamente.')
        return redirect('my_evaluation_history')

    return render(request, 'evaluations/diagnostic_form.html', {
        'competencies': competencies,
        'is_regular_self_eval': True
    })



# --- EVALUACIÓN ENTRE PARES (HU09) ---

@role_required(['ESTUDIANTE'])
def peer_evaluations(request):
    """Lista de compañeros del mismo equipo para evaluar entre pares (HU09)."""
    user_teams = Team.objects.filter(members=request.user).select_related('activity')
    
    peers_by_team = []
    for team in user_teams:
        teammates = team.members.exclude(id=request.user.id)
        for mate in teammates:
            completed_eval = Evaluation360.objects.filter(
                evaluator=request.user,
                evaluated=mate,
                evaluation_type=Evaluation360.EvaluationType.PARES,
                status=Evaluation360.Status.COMPLETADA
            ).exists()
            peers_by_team.append({
                'team': team,
                'peer': mate,
                'completed': completed_eval
            })
            
    return render(request, 'evaluations/peer_list.html', {
        'peers_by_team': peers_by_team
    })

@role_required(['ESTUDIANTE'])
def fill_peer_evaluation(request, peer_id):
    """Formulario para evaluar a un compañero de equipo (HU09)."""
    peer = get_object_or_404(CustomUser, pk=peer_id)
    
    # Verificar que compartan un equipo
    shared_team = Team.objects.filter(members=request.user).filter(members=peer).first()
    if not shared_team:
        messages.error(request, 'Solo puedes evaluar a compañeros que compartan un equipo contigo.')
        return redirect('peer_evaluations')

    competencies = Competency.objects.filter(is_active=True).prefetch_related('subcompetencies__rubrics')

    if request.method == 'POST':
        evaluation, _ = Evaluation360.objects.get_or_create(
            title=f'Evaluación de Pares - Equipo {shared_team.name}',
            competency=competencies.first(),
            evaluator=request.user,
            evaluated=peer,
            evaluation_type=Evaluation360.EvaluationType.PARES,
            period='PERIODO_ACTUAL'
        )

        for comp in competencies:
            for sub in comp.subcompetencies.filter(is_active=True):
                score_val = request.POST.get(f'subcompetency_{sub.id}')
                comment_val = request.POST.get(f'comment_{sub.id}', '')
                if score_val:
                    try:
                        score_num = float(score_val)
                        EvaluationScore.objects.update_or_create(
                            evaluation=evaluation,
                            subcompetency=sub,
                            defaults={'score': score_num, 'comment': comment_val}
                        )
                    except ValueError:
                        pass

        evaluation.status = Evaluation360.Status.COMPLETADA
        evaluation.completed_at = timezone.now()
        evaluation.save()

        messages.success(request, f'Evaluación realizada exitosamente para {peer.get_full_name()}.')
        return redirect('peer_evaluations')

    return render(request, 'evaluations/fill_evaluation.html', {
        'target_user': peer,
        'eval_type_display': 'Evaluación entre Pares (Anónima)',
        'competencies': competencies
    })


# --- EVALUACIÓN DOCENTE (HU10) ---

@role_required(['DOCENTE', 'COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def teacher_evaluations(request):
    """Lista de estudiantes inscritos en actividades del docente para ser evaluados (HU10)."""
    if request.user.role and request.user.role.name == 'DOCENTE':
        my_activities = Activity.objects.filter(instructor=request.user)
    else:
        my_activities = Activity.objects.all()

    students_to_eval = []
    for act in my_activities:
        enrollments = act.enrollments.filter(status=EnrollmentStatus.INSCRITO).select_related('student')
        for en in enrollments:
            completed_eval = Evaluation360.objects.filter(
                evaluator=request.user,
                evaluated=en.student,
                evaluation_type=Evaluation360.EvaluationType.DOCENTE,
                status=Evaluation360.Status.COMPLETADA
            ).exists()
            students_to_eval.append({
                'activity': act,
                'student': en.student,
                'completed': completed_eval
            })

    return render(request, 'evaluations/teacher_eval_list.html', {
        'students_to_eval': students_to_eval
    })

@role_required(['DOCENTE', 'COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def fill_teacher_evaluation(request, student_id, activity_id=None):
    """Formulario para que el docente evalúe las competencias de un estudiante (HU10)."""
    student = get_object_or_404(CustomUser, pk=student_id)
    activity = get_object_or_404(Activity, pk=activity_id) if activity_id else None
    competencies = Competency.objects.filter(is_active=True).prefetch_related('subcompetencies__rubrics')

    if request.method == 'POST':
        evaluation, _ = Evaluation360.objects.get_or_create(
            title=f'Evaluación Docente - {activity.title if activity else "General"}',
            competency=competencies.first(),
            evaluator=request.user,
            evaluated=student,
            evaluation_type=Evaluation360.EvaluationType.DOCENTE,
            period='PERIODO_ACTUAL'
        )

        for comp in competencies:
            for sub in comp.subcompetencies.filter(is_active=True):
                score_val = request.POST.get(f'subcompetency_{sub.id}')
                comment_val = request.POST.get(f'comment_{sub.id}', '')
                if score_val:
                    try:
                        score_num = float(score_val)
                        EvaluationScore.objects.update_or_create(
                            evaluation=evaluation,
                            subcompetency=sub,
                            defaults={'score': score_num, 'comment': comment_val}
                        )
                    except ValueError:
                        pass

        evaluation.status = Evaluation360.Status.COMPLETADA
        evaluation.completed_at = timezone.now()
        evaluation.save()

        messages.success(request, f'Evaluación registrada para {student.get_full_name()}.')
        return redirect('teacher_evaluations')

    return render(request, 'evaluations/fill_evaluation.html', {
        'target_user': student,
        'eval_type_display': f'Evaluación Docente ({activity.title if activity else "General"})',
        'competencies': competencies
    })


# --- EVALUACIÓN DE EMPRESA COLABORADORA / EMPLEADOR (HU11) ---

@role_required(['EMPRESA_COLABORADORA', 'COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def employer_evaluations(request):
    """Lista de estudiantes en prácticas asignados a la empresa (HU11)."""
    # En un esquema completo se consulta la relación Empresa-Estudiante (UserProfile.company_name o similar)
    # Por ahora traemos a los estudiantes activos para evaluación de prácticas
    students = CustomUser.objects.filter(role__name='ESTUDIANTE', is_active=True)
    
    students_to_eval = []
    for st in students:
        completed_eval = Evaluation360.objects.filter(
            evaluator=request.user,
            evaluated=st,
            evaluation_type=Evaluation360.EvaluationType.EMPLEADOR,
            status=Evaluation360.Status.COMPLETADA
        ).exists()
        students_to_eval.append({
            'student': st,
            'completed': completed_eval
        })
        
    return render(request, 'evaluations/employer_eval_list.html', {
        'students_to_eval': students_to_eval
    })

@role_required(['EMPRESA_COLABORADORA', 'COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def fill_employer_evaluation(request, student_id):
    """Formulario de evaluación en entorno laboral por parte del empleador (HU11)."""
    student = get_object_or_404(CustomUser, pk=student_id)
    competencies = Competency.objects.filter(is_active=True).prefetch_related('subcompetencies__rubrics')

    if request.method == 'POST':
        evaluation, _ = Evaluation360.objects.get_or_create(
            title='Evaluación de Prácticas Preprofesionales',
            competency=competencies.first(),
            evaluator=request.user,
            evaluated=student,
            evaluation_type=Evaluation360.EvaluationType.EMPLEADOR,
            period='PERIODO_PRACTICAS'
        )

        for comp in competencies:
            for sub in comp.subcompetencies.filter(is_active=True):
                score_val = request.POST.get(f'subcompetency_{sub.id}')
                comment_val = request.POST.get(f'comment_{sub.id}', '')
                if score_val:
                    try:
                        score_num = float(score_val)
                        EvaluationScore.objects.update_or_create(
                            evaluation=evaluation,
                            subcompetency=sub,
                            defaults={'score': score_num, 'comment': comment_val}
                        )
                    except ValueError:
                        pass

        evaluation.status = Evaluation360.Status.COMPLETADA
        evaluation.completed_at = timezone.now()
        evaluation.save()

        messages.success(request, f'Evaluación laboral registrada para {student.get_full_name()}.')
        return redirect('employer_evaluations')

    return render(request, 'evaluations/fill_evaluation.html', {
        'target_user': student,
        'eval_type_display': 'Evaluación de Prácticas Preprofesionales (Empresa)',
        'competencies': competencies
    })


# --- SEGUIMIENTO DE TUTORES ACADÉMICOS (HU13) ---

@role_required(['TUTOR_ACADEMICO', 'COORDINADOR_CARRERA', 'ADMINISTRADOR', 'BIENESTAR_UNIVERSITARIO'])
def tutor_students(request):
    """Listado de estudiantes tutorados con indicadores de avance y alertas (HU13)."""
    from django.db.models import Avg
    students = CustomUser.objects.filter(role__name='ESTUDIANTE', is_active=True)
    
    tutorados_list = []
    for st in students:
        avg_score = EvaluationScore.objects.filter(evaluation__evaluated=st).aggregate(avg=Avg('score'))['avg'] or 0.0
        avg_score = round(float(avg_score), 2)
        
        # Alerta si promedio < 5.0
        has_alert = avg_score > 0 and avg_score < 5.0
        
        tutorados_list.append({
            'student': st,
            'avg_score': avg_score,
            'has_alert': has_alert
        })
        
    return render(request, 'evaluations/tutor_students.html', {
        'tutorados_list': tutorados_list
    })

@role_required(['TUTOR_ACADEMICO', 'COORDINADOR_CARRERA', 'ADMINISTRADOR', 'BIENESTAR_UNIVERSITARIO'])
def tutor_student_detail(request, student_id):
    """Detalle de seguimiento 360° para un tutorado (HU13)."""
    from apps.evidences.models import Evidence
    student = get_object_or_404(CustomUser, pk=student_id)
    
    evaluations = Evaluation360.objects.filter(evaluated=student).select_related('evaluator').order_by('-created_at')
    scores = EvaluationScore.objects.filter(evaluation__evaluated=student).select_related('subcompetency__competency')
    evidences = Evidence.objects.filter(student=student)
    
    return render(request, 'evaluations/tutor_student_detail.html', {
        'student': student,
        'evaluations': evaluations,
        'scores': scores,
        'evidences': evidences
    })


# --- REPORTES ANALÍTICOS Y EXPORTACIÓN (HU16, HU17, HU18, HU21) ---

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'TUTOR_ACADEMICO', 'DOCENTE', 'BIENESTAR_UNIVERSITARIO'])
def reports_dashboard(request):
    """Panel analítico centralizado con visualización de tendencias y promedios grupales (HU18)."""
    from django.db.models import Avg
    from apps.users.models import CustomUser
    
    competencies = Competency.objects.filter(is_active=True)
    
    comp_metrics = []
    for comp in competencies:
        avg_score = EvaluationScore.objects.filter(
            subcompetency__competency=comp
        ).aggregate(avg=Avg('score'))['avg'] or 0.0
        
        students_count = EvaluationScore.objects.filter(
            subcompetency__competency=comp
        ).values('evaluation__evaluated').distinct().count()
        
        comp_metrics.append({
            'name': comp.name,
            'average': round(float(avg_score), 2),
            'students_count': students_count
        })
        
    global_average = EvaluationScore.objects.aggregate(avg=Avg('score'))['avg'] or 0.0
    total_evaluations = Evaluation360.objects.count()
    active_students = CustomUser.objects.filter(role__name='ESTUDIANTE', is_active=True).count()
        
    return render(request, 'evaluations/reports_dashboard.html', {
        'comp_metrics': comp_metrics,
        'global_average': global_average,
        'total_evaluations': total_evaluations,
        'active_students': active_students
    })

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'TUTOR_ACADEMICO', 'DOCENTE', 'BIENESTAR_UNIVERSITARIO'])
def export_csv_excel(request):
    """Exportar reporte de calificaciones en CSV/Excel (HU21)."""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reporte_habilidades_blandas.csv"'
    response.write('\ufeff')  # BOM UTF-8 para Microsoft Excel

    writer = csv.writer(response)
    writer.writerow(['Estudiante', 'Cédula', 'Correo', 'Competencia', 'Subcompetencia', 'Puntuación', 'Evaluador', 'Tipo Evaluación', 'Fecha'])

    scores = EvaluationScore.objects.select_related(
        'evaluation__evaluated', 'evaluation__evaluator', 'subcompetency__competency'
    ).all()

    for sc in scores:
        writer.writerow([
            sc.evaluation.evaluated.get_full_name(),
            sc.evaluation.evaluated.cedula or 'N/A',
            sc.evaluation.evaluated.email,
            sc.subcompetency.competency.name,
            sc.subcompetency.name,
            sc.score,
            sc.evaluation.evaluator.get_full_name(),
            sc.evaluation.get_evaluation_type_display(),
            sc.evaluation.created_at.strftime('%Y-%m-%d')
        ])

    return response


# --- HISTORIAL Y REPORTES DEL ESTUDIANTE (HU04, HU16, HU19, HU21) ---

@role_required(['ESTUDIANTE'])
def my_evaluation_history(request):
    """Consultar historial completo y auditable de evaluaciones del estudiante (HU19)."""
    from apps.evidences.models import Evidence
    from django.db.models import Avg

    student = request.user
    evaluations = Evaluation360.objects.filter(evaluated=student).select_related('evaluator', 'competency').order_by('-created_at')
    scores = EvaluationScore.objects.filter(evaluation__evaluated=student).select_related('subcompetency__competency', 'evaluation')
    evidences = Evidence.objects.filter(student=student).select_related('competency', 'activity')

    competencies = Competency.objects.filter(is_active=True)
    metrics = []
    for comp in competencies:
        avg = EvaluationScore.objects.filter(
            evaluation__evaluated=student,
            subcompetency__competency=comp
        ).aggregate(avg=Avg('score'))['avg'] or 0.0
        avg = round(float(avg), 2)

        if avg >= 8.5:
            level = 'Excelente'
            badge_class = 'bg-success'
        elif avg >= 7.0:
            level = 'Competente'
            badge_class = 'bg-primary'
        elif avg >= 5.0:
            level = 'En Desarrollo'
            badge_class = 'bg-warning'
        elif avg > 0:
            level = 'Inicial'
            badge_class = 'bg-danger'
        else:
            level = 'Sin Evaluar'
            badge_class = 'bg-secondary'

        metrics.append({
            'competency': comp,
            'avg_score': avg,
            'level': level,
            'badge_class': badge_class
        })

    return render(request, 'evaluations/my_evaluation_history.html', {
        'evaluations': evaluations,
        'scores': scores,
        'evidences': evidences,
        'metrics': metrics
    })


@role_required(['ESTUDIANTE'])
def export_my_report(request):
    """Exportar el reporte de seguimiento individual del estudiante en CSV/Excel (HU21)."""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv; charset=utf-8')
    filename = f"mi_reporte_habilidades_{request.user.username}.csv"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Estudiante', 'Competencia', 'Subcompetencia', 'Puntuación', 'Evaluador', 'Tipo de Evaluación', 'Fecha'])

    scores = EvaluationScore.objects.filter(
        evaluation__evaluated=request.user
    ).select_related('evaluation__evaluator', 'subcompetency__competency')

    for sc in scores:
        writer.writerow([
            request.user.get_full_name(),
            sc.subcompetency.competency.name,
            sc.subcompetency.name,
            sc.score,
            sc.evaluation.evaluator.get_full_name() if sc.evaluation.evaluator else 'Sistema',
            sc.evaluation.get_evaluation_type_display(),
            sc.evaluation.created_at.strftime('%Y-%m-%d %H:%M')
        ])

    return response


@role_required(['ESTUDIANTE'])
def print_my_report(request):
    """Vista de informe de seguimiento individual en formato listo para imprimir/PDF (HU21)."""
    from django.db.models import Avg
    student = request.user
    evaluations = Evaluation360.objects.filter(evaluated=student).select_related('evaluator').order_by('-created_at')
    scores = EvaluationScore.objects.filter(evaluation__evaluated=student).select_related('subcompetency__competency')

    competencies = Competency.objects.filter(is_active=True)
    metrics = []
    for comp in competencies:
        avg = EvaluationScore.objects.filter(
            evaluation__evaluated=student,
            subcompetency__competency=comp
        ).aggregate(avg=Avg('score'))['avg'] or 0.0
        metrics.append({
            'competency': comp,
            'avg_score': round(float(avg), 2)
        })

    return render(request, 'evaluations/student_report_print.html', {
        'student': student,
        'evaluations': evaluations,
        'scores': scores,
        'metrics': metrics,
        'now': timezone.now()
    })


@role_required(['ESTUDIANTE'])
def export_my_report_pdf(request):
    """Exportar informe individual del estudiante en archivo PDF descargable (HU21 / RF21)."""
    from django.db.models import Avg
    from .utils import render_to_pdf

    student = request.user
    evaluations = Evaluation360.objects.filter(evaluated=student).select_related('evaluator').order_by('-created_at')
    scores = EvaluationScore.objects.filter(evaluation__evaluated=student).select_related('subcompetency__competency')

    competencies = Competency.objects.filter(is_active=True)
    metrics = []
    for comp in competencies:
        avg = EvaluationScore.objects.filter(
            evaluation__evaluated=student,
            subcompetency__competency=comp
        ).aggregate(avg=Avg('score'))['avg'] or 0.0
        metrics.append({
            'competency': comp,
            'avg_score': round(float(avg), 2)
        })

    context = {
        'student': student,
        'evaluations': evaluations,
        'scores': scores,
        'metrics': metrics,
        'now': timezone.now()
    }
    filename = f"reporte_habilidades_{student.username}.pdf"
    pdf_response = render_to_pdf('evaluations/pdf/student_report_pdf.html', context, filename)
    if pdf_response:
        return pdf_response
    messages.error(request, 'Error al generar el archivo PDF del reporte.')
    return redirect('my_evaluation_history')


@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'DOCENTE'])
def export_group_report_pdf(request):
    """Exportar reporte grupal consolidado de competencias a PDF (HU21 / RF21)."""
    from django.db.models import Avg
    from apps.users.models import CustomUser
    from .utils import render_to_pdf

    students = CustomUser.objects.filter(role__name='ESTUDIANTE').select_related('role')
    competencies = Competency.objects.filter(is_active=True)

    group_data = []
    for st in students:
        st_scores = []
        total = 0
        count = 0
        for comp in competencies:
            avg = EvaluationScore.objects.filter(
                evaluation__evaluated=st,
                subcompetency__competency=comp
            ).aggregate(avg=Avg('score'))['avg'] or 0.0
            st_scores.append({'competency': comp, 'avg': round(float(avg), 2)})
            if avg > 0:
                total += avg
                count += 1
        overall = round(float(total / count), 2) if count > 0 else 0.0
        group_data.append({
            'student': st,
            'scores': st_scores,
            'overall': overall
        })

    context = {
        'group_data': group_data,
        'competencies': competencies,
        'now': timezone.now()
    }
    filename = "reporte_grupal_competencias.pdf"
    pdf_response = render_to_pdf('evaluations/pdf/group_report_pdf.html', context, filename)
    if pdf_response:
        return pdf_response
    messages.error(request, 'Error al generar el PDF del reporte grupal.')
    return redirect('reports_dashboard')


@role_required(['BIENESTAR_UNIVERSITARIO', 'COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def wellness_alerts(request):
    """Dashboard de Alertas de Bajo Desempeño Competencial para Bienestar Universitario (HU22 / RF22)."""
    from django.db.models import Avg
    from apps.users.models import CustomUser

    students = CustomUser.objects.filter(role__name='ESTUDIANTE').select_related('role')
    competencies = Competency.objects.filter(is_active=True)

    alerts = []
    for st in students:
        low_competencies = []
        total_score = 0
        evaluated_count = 0
        
        for comp in competencies:
            avg = EvaluationScore.objects.filter(
                evaluation__evaluated=st,
                subcompetency__competency=comp
            ).aggregate(avg=Avg('score'))['avg'] or 0.0
            if avg > 0:
                total_score += avg
                evaluated_count += 1
                if avg < 2.5:  # Nivel Inicial o con dificultades
                    low_competencies.append({
                        'competency': comp.name,
                        'score': round(float(avg), 2)
                    })

        overall_avg = round(float(total_score / evaluated_count), 2) if evaluated_count > 0 else 0.0

        if len(low_competencies) >= 2 or (overall_avg > 0 and overall_avg < 2.0):
            alert_level = 'ALTA'  # Alerta Roja
            badge_class = 'danger'
        elif len(low_competencies) == 1 or (overall_avg >= 2.0 and overall_avg < 2.8):
            alert_level = 'MEDIA'  # Alerta Amarilla
            badge_class = 'warning'
        else:
            continue  # Sin alerta activa

        alerts.append({
            'student': st,
            'overall_avg': overall_avg,
            'low_competencies': low_competencies,
            'alert_level': alert_level,
            'badge_class': badge_class,
            'evaluated_count': evaluated_count
        })

    return render(request, 'evaluations/wellness_alerts.html', {
        'alerts': alerts
    })


@role_required(['ADMINISTRADOR', 'COORDINADOR_CARRERA'])
def audit_log_list(request):
    """Vista para consultar y filtrar la Bitácora de Auditoría inmutable para el Administrador (HU23 / RF19)."""
    from .models import AuditLog

    logs = AuditLog.objects.select_related('user').order_by('-timestamp')

    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    query = request.GET.get('q', '')

    if action_filter:
        logs = logs.filter(action__icontains=action_filter)
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    if query:
        logs = logs.filter(model_name__icontains=query)

    logs = logs[:100]  # Limitar a los 100 registros más recientes

    return render(request, 'evaluations/audit_log_list.html', {
        'logs': logs,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'query': query
    })


@role_required(['GRADUADO', 'ESTUDIANTE', 'ADMINISTRADOR'])
def graduate_feedback_create(request):
    """Formulario para que los graduados envíen su retroalimentación laboral sobre habilidades blandas (RF12)."""
    from .forms import GraduateFeedbackForm
    from .utils import log_action

    if request.method == 'POST':
        form = GraduateFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.graduate = request.user
            feedback.save()

            log_action(
                user=request.user,
                action='CREAR_RETROALIMENTACION_GRADUADO',
                model_name='GraduateFeedback',
                object_id=feedback.id,
                changes={
                    'company': feedback.company_name,
                    'competency': feedback.competency.name if feedback.competency else ''
                },
                request=request
            )

            messages.success(request, '¡Muchas gracias! Tu retroalimentación laboral ha sido registrada exitosamente.')
            return redirect('dashboard')
    else:
        form = GraduateFeedbackForm()

    return render(request, 'evaluations/graduate_feedback_form.html', {
        'form': form
    })


@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'DOCENTE'])
def graduate_feedback_list(request):
    """Panel de consulta de la retroalimentación de graduados sobre la aplicación de competencias en el mercado laboral (RF12)."""
    from .models import GraduateFeedback

    feedbacks = GraduateFeedback.objects.select_related('graduate', 'competency').all()
    return render(request, 'evaluations/graduate_feedback_list.html', {
        'feedbacks': feedbacks
    })





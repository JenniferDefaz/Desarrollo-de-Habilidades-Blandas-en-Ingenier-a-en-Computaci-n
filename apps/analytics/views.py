import csv
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Avg, Count
from core.decorators import role_required
from apps.users.models import CustomUser
from apps.competencies.models import Competency
from .models import StudentMetric, CohortReport

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'TUTOR_ACADEMICO', 'BIENESTAR_UNIVERSITARIO'])
def analytics_dashboard(request):
    """Panel de control principal de analíticas (HU18)."""
    # KPI 1: Promedio general por competencia
    competencies = Competency.objects.filter(is_active=True)
    comp_labels = []
    comp_scores = []
    
    for comp in competencies:
        avg = StudentMetric.objects.filter(competency=comp).aggregate(Avg('average_score'))['average_score__avg']
        comp_labels.append(comp.name)
        comp_scores.append(round(avg, 2) if avg else 0)
        
    # KPI 2: Total estudiantes evaluados
    total_students = StudentMetric.objects.values('student').distinct().count()
    total_evaluations = StudentMetric.objects.aggregate(Count('id'))['id__count'] or 0
    
    context = {
        'comp_labels': comp_labels,
        'comp_scores': comp_scores,
        'total_students': total_students,
        'total_evaluations': total_evaluations
    }
    return render(request, 'analytics/dashboard.html', context)


@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'TUTOR_ACADEMICO'])
def student_tracking_report(request):
    """Reporte de seguimiento individual (HU16)."""
    students = CustomUser.objects.filter(role__name='ESTUDIANTE', is_active=True)
    selected_student_id = request.GET.get('student_id')
    metrics = []
    selected_student = None

    if selected_student_id:
        selected_student = CustomUser.objects.filter(id=selected_student_id).first()
        if selected_student:
            metrics = StudentMetric.objects.filter(student=selected_student).select_related('competency')

    context = {
        'students': students,
        'metrics': metrics,
        'selected_student': selected_student
    }
    return render(request, 'analytics/student_tracking.html', context)


@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'TUTOR_ACADEMICO'])
def cohort_report_view(request):
    """Reportes grupales por cohorte/semestre (HU17)."""
    reports = CohortReport.objects.all().order_by('-created_at')
    return render(request, 'analytics/cohort_report.html', {'reports': reports})


@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR', 'TUTOR_ACADEMICO'])
def export_report(request):
    """Exportación básica de reporte grupal a CSV/Excel (RF21)."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_competencias.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Estudiante', 'Email', 'Competencia', 'Puntaje Promedio', 'Nivel Actual'])
    
    metrics = StudentMetric.objects.select_related('student', 'competency').all()
    for metric in metrics:
        writer.writerow([
            metric.student.get_full_name(),
            metric.student.email,
            metric.competency.name,
            metric.average_score,
            metric.get_current_level_display()
        ])
        
    return response

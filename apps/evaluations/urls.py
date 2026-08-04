from django.urls import path
from . import views

urlpatterns = [
    # Diagnóstico inicial (HU03)
    path('diagnostico-inicial/', views.initial_diagnostic, name='initial_diagnostic'),
    
    # Autoevaluación regular (HU04)
    path('autoevaluacion/', views.self_evaluation, name='self_evaluation'),
    
    # Evaluación entre pares (HU09)
    path('pares/', views.peer_evaluations, name='peer_evaluations'),
    path('pares/<int:peer_id>/evaluar/', views.fill_peer_evaluation, name='fill_peer_evaluation'),
    
    # Evaluación docente (HU10)
    path('docente/', views.teacher_evaluations, name='teacher_evaluations'),
    path('docente/<int:student_id>/evaluar/', views.fill_teacher_evaluation, name='fill_teacher_evaluation'),
    path('docente/<int:student_id>/actividad/<int:activity_id>/evaluar/', views.fill_teacher_evaluation, name='fill_teacher_activity_evaluation'),
    
    # Evaluación empleador (HU11)
    path('empleador/', views.employer_evaluations, name='employer_evaluations'),
    path('empleador/<int:student_id>/evaluar/', views.fill_employer_evaluation, name='fill_employer_evaluation'),
    
    # Tutores académicos (HU13)
    path('tutorados/', views.tutor_students, name='tutor_students'),
    path('tutorados/<int:student_id>/', views.tutor_student_detail, name='tutor_student_detail'),
    
    # Reportes analíticos y exportación general (HU16, HU17, HU18, HU21)
    path('reportes/', views.reports_dashboard, name='reports_dashboard'),
    path('reportes/exportar-excel/', views.export_csv_excel, name='export_csv_excel'),

    # Historial y Reportes propios del Estudiante (HU04, HU16, HU19, HU21)
    path('mi-historial/', views.my_evaluation_history, name='my_evaluation_history'),
    path('exportar-mi-reporte/', views.export_my_report, name='export_my_report'),
    path('exportar-mi-reporte-pdf/', views.export_my_report_pdf, name='export_my_report_pdf'),
    path('imprimir-mi-reporte/', views.print_my_report, name='print_my_report'),
    path('reportes/exportar-pdf/', views.export_group_report_pdf, name='export_group_report_pdf'),

    # Alertas de Bienestar Universitario (HU22 / RF22)
    path('bienestar/alertas/', views.wellness_alerts, name='wellness_alerts'),

    # Bitácora de Auditoría (HU23 / RF19)
    path('bitacora/', views.audit_log_list, name='audit_log_list'),

    # Retroalimentación de Graduados (RF12)
    path('graduados/retroalimentacion/', views.graduate_feedback_create, name='graduate_feedback_create'),
    path('graduados/respuestas/', views.graduate_feedback_list, name='graduate_feedback_list'),
]



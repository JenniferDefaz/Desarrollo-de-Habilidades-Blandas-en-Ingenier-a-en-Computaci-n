from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.analytics_dashboard, name='analytics_dashboard'),
    path('seguimiento-estudiante/', views.student_tracking_report, name='student_tracking_report'),
    path('reportes-cohorte/', views.cohort_report_view, name='cohort_report_view'),
    path('exportar/', views.export_report, name='export_report'),
]

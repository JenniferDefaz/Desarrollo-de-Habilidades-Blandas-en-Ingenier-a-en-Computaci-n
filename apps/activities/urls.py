from django.urls import path
from . import views

urlpatterns = [
    # Gestión docente
    path('', views.activity_list, name='activity_list'),
    path('crear/', views.activity_create, name='activity_create'),
    path('<int:pk>/', views.activity_detail, name='activity_detail'),
    path('<int:pk>/editar/', views.activity_update, name='activity_update'),
    path('<int:pk>/eliminar/', views.activity_delete, name='activity_delete'),
    
    # Retos colaborativos (HU14)
    path('retos/', views.challenges_list, name='challenges_list'),
    path('<int:activity_id>/equipos/', views.manage_teams, name='manage_teams'),
    
    # Estudiantes
    path('catalogo/', views.student_activities, name='student_activities'),
    path('<int:pk>/inscribir/', views.enroll_activity, name='enroll_activity'),
    path('<int:pk>/cancelar/', views.cancel_enrollment, name='cancel_enrollment'),
    
    # Gestión de Mentores (HU12)
    path('<int:pk>/postular-mentor/', views.apply_as_mentor, name='apply_as_mentor'),
    path('<int:activity_id>/mentores/', views.manage_mentors, name='manage_mentors'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    path('teacher_dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('coordinator_dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('graduate_dashboard/', views.graduate_dashboard, name='graduate_dashboard'),
    path('tutor_dashboard/', views.tutor_dashboard, name='tutor_dashboard'),
    path('employer_dashboard/', views.employer_dashboard, name='employer_dashboard'),
    path('bienestar_dashboard/', views.bienestar_dashboard, name='bienestar_dashboard'),
    path('tutor/nota/<int:student_id>/', views.add_tutor_note, name='add_tutor_note'),
    path('api/check-session/', views.check_session_status, name='check_session_status'),
]

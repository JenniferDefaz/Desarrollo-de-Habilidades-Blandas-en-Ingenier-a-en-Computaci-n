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
    path('api/check-session/', views.check_session_status, name='check_session_status'),
]

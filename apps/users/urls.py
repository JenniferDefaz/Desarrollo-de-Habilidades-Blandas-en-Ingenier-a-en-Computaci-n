from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('crear/', views.user_create, name='user_create'),
    path('editar/<int:pk>/', views.user_update, name='user_update'),
    path('eliminar/<int:pk>/', views.user_delete, name='user_delete'),
    path('perfil/', views.profile_view, name='user_profile'),
    path('configuracion/', views.settings_view, name='user_settings'),
    path('configuracion-general/', views.system_settings_view, name='system_settings_view'),
    path('soporte/', views.support_ticket_list, name='support_ticket_list'),
    path('soporte/nuevo/', views.support_ticket_create, name='support_ticket_create'),
    path('soporte/<int:pk>/', views.support_ticket_detail, name='support_ticket_detail'),
]


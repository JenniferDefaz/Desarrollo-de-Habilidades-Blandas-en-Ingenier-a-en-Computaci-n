from django.urls import path
from . import views

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('<int:pk>/leer/', views.mark_as_read, name='notification_mark_as_read'),
    path('marcar-todas-leidas/', views.mark_all_as_read, name='notification_mark_all_read'),
]

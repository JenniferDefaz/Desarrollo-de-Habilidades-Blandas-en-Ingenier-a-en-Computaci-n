from django.urls import path
from . import views

urlpatterns = [
    # Competencias
    path('', views.competency_list, name='competency_list'),
    path('crear/', views.competency_create, name='competency_create'),
    path('<int:pk>/', views.competency_detail, name='competency_detail'),
    path('<int:pk>/editar/', views.competency_update, name='competency_update'),
    path('<int:pk>/eliminar/', views.competency_delete, name='competency_delete'),
    
    # Subcompetencias
    path('<int:competency_pk>/subcompetencias/crear/', views.subcompetency_create, name='subcompetency_create'),
    path('subcompetencias/<int:pk>/editar/', views.subcompetency_update, name='subcompetency_update'),
    path('subcompetencias/<int:pk>/eliminar/', views.subcompetency_delete, name='subcompetency_delete'),
    
    # Rúbricas
    path('subcompetencias/<int:subcompetency_pk>/rubricas/crear/', views.rubric_create, name='rubric_create'),
    path('rubricas/<int:pk>/editar/', views.rubric_update, name='rubric_update'),
    path('rubricas/<int:pk>/eliminar/', views.rubric_delete, name='rubric_delete'),
]

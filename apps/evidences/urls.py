from django.urls import path
from . import views

urlpatterns = [
    # Estudiante
    path('mis-evidencias/', views.my_evidences, name='my_evidences'),
    path('subir/', views.upload_evidence, name='upload_evidence'),
    path('<int:pk>/editar/', views.upload_evidence, name='edit_evidence'),
    path('<int:pk>/eliminar/', views.delete_evidence, name='delete_evidence'),
    
    # Docente
    path('bandeja-revision/', views.review_inbox, name='review_inbox'),
    path('<int:pk>/revisar/', views.review_evidence, name='review_evidence'),
]

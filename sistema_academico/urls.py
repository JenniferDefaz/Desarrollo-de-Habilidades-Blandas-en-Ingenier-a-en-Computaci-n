from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('usuarios/', include('apps.users.urls')),
    path('competencias/', include('apps.competencies.urls')),
    path('actividades/', include('apps.activities.urls')),
    path('evaluaciones/', include('apps.evaluations.urls')),
    path('evidencias/', include('apps.evidences.urls')),
    path('notificaciones/', include('apps.notifications.urls')),
    path('analiticas/', include('apps.analytics.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


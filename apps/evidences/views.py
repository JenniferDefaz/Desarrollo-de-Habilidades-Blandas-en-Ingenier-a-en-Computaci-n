from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from core.decorators import role_required
from .models import Evidence, EvidenceStatus
from .forms import EvidenceForm, ReviewForm

# --- VISTAS DE ESTUDIANTE (HU07) ---

@role_required(['ESTUDIANTE'])
def my_evidences(request):
    """Portafolio de evidencias del estudiante."""
    evidences = Evidence.objects.filter(student=request.user).select_related('competency', 'activity')
    return render(request, 'evidences/my_evidences.html', {'evidences': evidences})

@role_required(['ESTUDIANTE'])
def upload_evidence(request, pk=None):
    """Subir o editar una evidencia de aprendizaje."""
    evidence = get_object_or_404(Evidence, pk=pk, student=request.user) if pk else None
    activity_id = request.GET.get('activity')
    
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES, instance=evidence, user=request.user, activity_id=activity_id)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.student = request.user
            if ev.activity:
                ev.competency = ev.activity.competency
            ev.status = EvidenceStatus.PENDIENTE
            ev.save()
            messages.success(request, 'Evidencia subida exitosamente. Está pendiente de revisión.')
            return redirect('my_evidences')
    else:
        initial_data = {}
        if activity_id:
            initial_data['activity'] = activity_id
            
        form = EvidenceForm(instance=evidence, user=request.user, activity_id=activity_id, initial=initial_data)
        
    return render(request, 'evidences/evidence_form.html', {'form': form, 'obj': evidence})

@role_required(['ESTUDIANTE'])
def delete_evidence(request, pk):
    """Eliminar una evidencia propia si aún no ha sido aprobada."""
    evidence = get_object_or_404(Evidence, pk=pk, student=request.user)
    if request.method == 'POST':
        evidence.delete()
        messages.success(request, 'Evidencia eliminada correctamente.')
    return redirect('my_evidences')


# --- VISTAS DE DOCENTE / COORDINADOR (HU08) ---

@role_required(['DOCENTE', 'COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def review_inbox(request):
    """Bandeja de evidencias pendientes por revisar."""
    pending_evidences = Evidence.objects.filter(
        status=EvidenceStatus.PENDIENTE
    ).select_related('student', 'competency', 'activity')
    
    reviewed_evidences = Evidence.objects.exclude(
        status=EvidenceStatus.PENDIENTE
    ).select_related('student', 'competency', 'activity')[:15]
    
    return render(request, 'evidences/review_inbox.html', {
        'pending_evidences': pending_evidences,
        'reviewed_evidences': reviewed_evidences
    })

@role_required(['DOCENTE', 'COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def review_evidence(request, pk):
    """Revisar, evaluar y dejar retroalimentación a una evidencia (HU08)."""
    evidence = get_object_or_404(Evidence, pk=pk)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            evidence.status = form.cleaned_data['status']
            evidence.review_comment = form.cleaned_data['review_comment']
            evidence.reviewed_by = request.user
            evidence.reviewed_at = timezone.now()
            evidence.save()
            messages.success(request, f'Evidencia de {evidence.student.get_full_name()} revisada exitosamente.')
            return redirect('review_inbox')
    else:
        form = ReviewForm(initial={
            'status': evidence.status if evidence.status != EvidenceStatus.PENDIENTE else EvidenceStatus.APROBADA,
            'review_comment': evidence.review_comment
        })
        
    return render(request, 'evidences/review_form.html', {
        'evidence': evidence,
        'form': form
    })

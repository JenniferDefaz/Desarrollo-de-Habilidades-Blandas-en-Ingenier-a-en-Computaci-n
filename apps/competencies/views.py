from django.shortcuts import render, redirect, get_object_or_404
from core.decorators import role_required
from django.contrib import messages
from .models import Competency, Subcompetency, Rubric
from .forms import CompetencyForm, SubcompetencyForm, RubricForm

# --- COMPETENCIES ---

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def competency_list(request):
    competencies = Competency.objects.all()
    return render(request, 'competencies/competency_list.html', {'competencies': competencies})

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def competency_detail(request, pk):
    competency = get_object_or_404(Competency, pk=pk)
    # Fetch related subcompetencies and their rubrics efficiently
    subcompetencies = competency.subcompetencies.prefetch_related('rubrics').all()
    return render(request, 'competencies/competency_detail.html', {
        'competency': competency,
        'subcompetencies': subcompetencies
    })

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def competency_create(request):
    if request.method == 'POST':
        form = CompetencyForm(request.POST)
        if form.is_valid():
            comp = form.save()
            messages.success(request, 'Competencia creada exitosamente.')
            return redirect('competency_detail', pk=comp.pk)
    else:
        form = CompetencyForm()
    return render(request, 'competencies/competency_form.html', {'form': form, 'obj': None})

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def competency_update(request, pk):
    competency = get_object_or_404(Competency, pk=pk)
    if request.method == 'POST':
        form = CompetencyForm(request.POST, instance=competency)
        if form.is_valid():
            form.save()
            messages.success(request, 'Competencia actualizada exitosamente.')
            return redirect('competency_detail', pk=competency.pk)
    else:
        form = CompetencyForm(instance=competency)
    return render(request, 'competencies/competency_form.html', {'form': form, 'obj': competency})

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def competency_delete(request, pk):
    competency = get_object_or_404(Competency, pk=pk)
    if request.method == 'POST':
        competency.delete()
        messages.success(request, 'Competencia eliminada exitosamente.')
    return redirect('competency_list')

# --- SUBCOMPETENCIES ---

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def subcompetency_create(request, competency_pk):
    competency = get_object_or_404(Competency, pk=competency_pk)
    if request.method == 'POST':
        form = SubcompetencyForm(request.POST)
        if form.is_valid():
            subcomp = form.save(commit=False)
            subcomp.competency = competency
            subcomp.save()
            messages.success(request, 'Subcompetencia añadida exitosamente.')
            return redirect('competency_detail', pk=competency.pk)
    else:
        form = SubcompetencyForm()
    return render(request, 'competencies/subcompetency_form.html', {
        'form': form, 
        'competency': competency,
        'obj': None
    })

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def subcompetency_update(request, pk):
    subcomp = get_object_or_404(Subcompetency, pk=pk)
    if request.method == 'POST':
        form = SubcompetencyForm(request.POST, instance=subcomp)
        if form.is_valid():
            form.save()
            messages.success(request, 'Subcompetencia actualizada.')
            return redirect('competency_detail', pk=subcomp.competency.pk)
    else:
        form = SubcompetencyForm(instance=subcomp)
    return render(request, 'competencies/subcompetency_form.html', {
        'form': form, 
        'competency': subcomp.competency,
        'obj': subcomp
    })

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def subcompetency_delete(request, pk):
    subcomp = get_object_or_404(Subcompetency, pk=pk)
    comp_pk = subcomp.competency.pk
    if request.method == 'POST':
        subcomp.delete()
        messages.success(request, 'Subcompetencia eliminada.')
    return redirect('competency_detail', pk=comp_pk)

# --- RUBRICS ---

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def rubric_create(request, subcompetency_pk):
    subcomp = get_object_or_404(Subcompetency, pk=subcompetency_pk)
    if request.method == 'POST':
        form = RubricForm(request.POST)
        if form.is_valid():
            rubric = form.save(commit=False)
            rubric.subcompetency = subcomp
            # Check for unique level
            if Rubric.objects.filter(subcompetency=subcomp, level=rubric.level).exists():
                messages.error(request, f'Ya existe una rúbrica con el nivel {rubric.get_level_display()} para esta subcompetencia.')
            else:
                rubric.save()
                messages.success(request, 'Rúbrica añadida exitosamente.')
                return redirect('competency_detail', pk=subcomp.competency.pk)
    else:
        form = RubricForm()
    return render(request, 'competencies/rubric_form.html', {
        'form': form, 
        'subcompetency': subcomp,
        'obj': None
    })

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def rubric_update(request, pk):
    rubric = get_object_or_404(Rubric, pk=pk)
    if request.method == 'POST':
        form = RubricForm(request.POST, instance=rubric)
        if form.is_valid():
            # Check for unique level if changed
            new_level = form.cleaned_data.get('level')
            if new_level != rubric.level and Rubric.objects.filter(subcompetency=rubric.subcompetency, level=new_level).exists():
                messages.error(request, f'Ya existe una rúbrica con el nivel seleccionado.')
            else:
                form.save()
                messages.success(request, 'Rúbrica actualizada.')
                return redirect('competency_detail', pk=rubric.subcompetency.competency.pk)
    else:
        form = RubricForm(instance=rubric)
    return render(request, 'competencies/rubric_form.html', {
        'form': form, 
        'subcompetency': rubric.subcompetency,
        'obj': rubric
    })

@role_required(['COORDINADOR_CARRERA', 'ADMINISTRADOR'])
def rubric_delete(request, pk):
    rubric = get_object_or_404(Rubric, pk=pk)
    comp_pk = rubric.subcompetency.competency.pk
    if request.method == 'POST':
        rubric.delete()
        messages.success(request, 'Rúbrica eliminada.')
    return redirect('competency_detail', pk=comp_pk)

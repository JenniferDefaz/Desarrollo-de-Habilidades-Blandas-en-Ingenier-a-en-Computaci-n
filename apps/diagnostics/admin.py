from django.contrib import admin
from .models import DiagnosticQuestion, DiagnosticResult


@admin.register(DiagnosticQuestion)
class DiagnosticQuestionAdmin(admin.ModelAdmin):
    list_display = ('order', 'text', 'competency', 'is_active')
    list_filter = ('competency', 'is_active')
    ordering = ('order',)


@admin.register(DiagnosticResult)
class DiagnosticResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'question', 'score', 'evaluated_at')
    list_filter = ('question__competency',)
    search_fields = ('student__username', 'student__first_name')

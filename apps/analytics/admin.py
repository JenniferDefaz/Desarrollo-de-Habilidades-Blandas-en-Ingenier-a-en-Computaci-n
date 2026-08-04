from django.contrib import admin
from .models import StudentMetric, CohortReport


@admin.register(StudentMetric)
class StudentMetricAdmin(admin.ModelAdmin):
    list_display = ('student', 'competency', 'average_score', 'evaluations_count', 'current_level', 'last_updated')
    list_filter = ('current_level', 'competency')
    search_fields = ('student__username', 'student__first_name')


@admin.register(CohortReport)
class CohortReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'period', 'generated_by', 'created_at')
    list_filter = ('period',)
    search_fields = ('title',)

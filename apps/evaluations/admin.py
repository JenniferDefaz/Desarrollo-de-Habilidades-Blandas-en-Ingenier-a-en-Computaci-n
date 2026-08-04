from django.contrib import admin
from .models import Evaluation360, EvaluationScore, AuditLog


class EvaluationScoreInline(admin.TabularInline):
    model = EvaluationScore
    extra = 1


@admin.register(Evaluation360)
class Evaluation360Admin(admin.ModelAdmin):
    list_display = ('title', 'evaluation_type', 'evaluator', 'evaluated', 'status', 'period', 'created_at')
    list_filter = ('evaluation_type', 'status', 'period')
    search_fields = ('title', 'evaluator__username', 'evaluated__username')
    inlines = [EvaluationScoreInline]


@admin.register(EvaluationScore)
class EvaluationScoreAdmin(admin.ModelAdmin):
    list_display = ('evaluation', 'subcompetency', 'score')
    list_filter = ('evaluation__evaluation_type',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'model_name', 'object_id', 'user', 'timestamp')
    list_filter = ('action', 'model_name')
    search_fields = ('model_name',)
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'changes', 'ip_address', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

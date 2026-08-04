from django.contrib import admin
from .models import Activity, Team, Enrollment, Challenge


class ChallengeInline(admin.StackedInline):
    model = Challenge
    can_delete = True
    extra = 0


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('title', 'activity_type', 'competency', 'instructor', 'start_date', 'end_date', 'is_active')
    list_filter = ('activity_type', 'is_active', 'competency')
    search_fields = ('title',)
    inlines = [ChallengeInline]


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity', 'created_at')
    filter_horizontal = ('members',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity', 'team', 'status', 'enrolled_at')
    list_filter = ('status', 'activity')
    search_fields = ('student__username', 'student__first_name')


@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('activity', 'due_date', 'max_score')

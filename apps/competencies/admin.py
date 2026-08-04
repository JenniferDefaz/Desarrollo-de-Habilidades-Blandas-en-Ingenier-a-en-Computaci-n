from django.contrib import admin
from .models import Competency, Subcompetency, Rubric


class SubcompetencyInline(admin.TabularInline):
    model = Subcompetency
    extra = 1


class RubricInline(admin.TabularInline):
    model = Rubric
    extra = 1


@admin.register(Competency)
class CompetencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    inlines = [SubcompetencyInline]


@admin.register(Subcompetency)
class SubcompetencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'competency', 'is_active')
    list_filter = ('competency', 'is_active')
    search_fields = ('name',)
    inlines = [RubricInline]


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
    list_display = ('subcompetency', 'level', 'min_score', 'max_score')
    list_filter = ('level',)

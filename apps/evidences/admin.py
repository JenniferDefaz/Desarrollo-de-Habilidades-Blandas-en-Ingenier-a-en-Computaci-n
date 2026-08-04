from django.contrib import admin
from .models import Evidence, FileMetadata


class FileMetadataInline(admin.TabularInline):
    model = FileMetadata
    extra = 1


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'competency', 'evidence_type', 'status', 'uploaded_at')
    list_filter = ('evidence_type', 'status', 'competency')
    search_fields = ('title', 'student__username', 'student__first_name')
    inlines = [FileMetadataInline]


@admin.register(FileMetadata)
class FileMetadataAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'evidence', 'file_size', 'mime_type', 'uploaded_at')

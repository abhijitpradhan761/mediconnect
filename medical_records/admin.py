from django.contrib import admin
from .models import MedicalDocument, ConsultationNote


@admin.register(MedicalDocument)
class MedicalDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'document_type', 'file_size_bytes', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title', 'patient__username', 'patient__first_name', 'patient__last_name', 'description')
    readonly_fields = ('file_size_bytes', 'uploaded_at', 'updated_at')


@admin.register(ConsultationNote)
class ConsultationNoteAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'doctor', 'follow_up_date', 'created_at')
    list_filter = ('created_at', 'follow_up_date')
    search_fields = ('appointment__patient__username', 'doctor__user__username', 'clinical_observations')
    readonly_fields = ('created_at', 'updated_at')

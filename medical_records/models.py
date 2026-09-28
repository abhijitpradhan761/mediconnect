from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import os


def patient_document_upload_path(instance, filename):
    """
    Secure isolated upload path per patient.
    Directory traversal protection by using base name.
    """
    safe_filename = os.path.basename(filename)
    return f'patients/{instance.patient.pk}/documents/{safe_filename}'


ALLOWED_EXTENSIONS = ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'txt']
MAX_FILE_SIZE_MB = 10


class MedicalDocument(models.Model):
    """
    Medical documents uploaded by patients or associated with appointments.
    Strict file validation and secure permission checking are enforced.
    """
    class DocumentType(models.TextChoices):
        LAB_REPORT = 'LAB_REPORT', 'Lab Report'
        PRESCRIPTION = 'PRESCRIPTION', 'Prescription'
        IMAGING = 'IMAGING', 'Imaging / X-Ray / Scan'
        DISCHARGE_SUMMARY = 'DISCHARGE_SUMMARY', 'Discharge Summary'
        INSURANCE = 'INSURANCE', 'Insurance Document'
        OTHER = 'OTHER', 'Other Medical Document'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='medical_documents',
        limit_choices_to={'role': 'PATIENT'}
    )
    appointment = models.ForeignKey(
        'appointments.Appointment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        help_text='Optional appointment this document relates to.'
    )
    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        default=DocumentType.OTHER
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=patient_document_upload_path)
    file_size_bytes = models.PositiveBigIntegerField(default=0, editable=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Medical Document'
        verbose_name_plural = 'Medical Documents'

    def clean(self):
        if self.file:
            ext = self.file.name.rsplit('.', 1)[-1].lower() if '.' in self.file.name else ''
            if ext not in ALLOWED_EXTENSIONS:
                raise ValidationError(
                    f"Unsupported file format '.{ext}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
                )
            if hasattr(self.file, 'size') and self.file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise ValidationError(f"File size exceeds maximum allowed limit of {MAX_FILE_SIZE_MB}MB.")

    def save(self, *args, **kwargs):
        if self.file and hasattr(self.file, 'size'):
            self.file_size_bytes = self.file.size
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()}) - {self.patient.get_full_name()}"


class ConsultationNote(models.Model):
    """
    Clinical consultation notes created by attending doctor after consultation.
    Medical ethical note: These records store clinical observations and follow-up guidance,
    not autonomous diagnosis.
    """
    appointment = models.OneToOneField(
        'appointments.Appointment',
        on_delete=models.CASCADE,
        related_name='consultation_note'
    )
    doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='consultation_notes'
    )
    clinical_observations = models.TextField(
        help_text='Objective clinical observations and consultation summary.'
    )
    follow_up_instructions = models.TextField(
        blank=True,
        help_text='Recommended lifestyle guidance, tests, or follow-up directions.'
    )
    follow_up_date = models.DateField(
        null=True,
        blank=True,
        help_text='Recommended follow-up date if applicable.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Consultation Note'
        verbose_name_plural = 'Consultation Notes'

    def __str__(self):
        return f"Consultation Note for Appointment #{self.appointment.pk} (Dr. {self.doctor.user.get_full_name()})"

from django import forms
from .models import MedicalDocument, ConsultationNote
from appointments.models import Appointment


class MedicalDocumentUploadForm(forms.ModelForm):
    """
    Form for uploading a medical document.
    Allows associating document with patient's own appointments.
    """
    class Meta:
        model = MedicalDocument
        fields = ['title', 'document_type', 'file', 'description', 'appointment']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Blood Test Results, MRI Lumbar Spine'}),
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Additional context or findings noted in report...'}),
            'appointment': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        if patient:
            self.fields['appointment'].queryset = Appointment.objects.filter(
                patient=patient
            ).order_by('-appointment_date')
            self.fields['appointment'].required = False
            self.fields['appointment'].empty_label = "— None / General Health Document —"


class ConsultationNoteForm(forms.ModelForm):
    """
    Doctor's clinical note entry form.
    """
    class Meta:
        model = ConsultationNote
        fields = ['clinical_observations', 'follow_up_instructions', 'follow_up_date']
        widgets = {
            'clinical_observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Objective clinical assessment, symptoms discussed, and physical findings...'
            }),
            'follow_up_instructions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Medication instructions, lifestyle advice, diet, or specialist referral...'
            }),
            'follow_up_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

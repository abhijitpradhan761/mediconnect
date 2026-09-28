from rest_framework import serializers
from .models import MedicalDocument, ConsultationNote
from accounts.serializers import UserSerializer


class MedicalDocumentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.get_full_name', read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)

    class Meta:
        model = MedicalDocument
        fields = [
            'id', 'patient', 'patient_name', 'appointment', 'document_type',
            'document_type_display', 'title', 'description', 'file',
            'file_size_bytes', 'uploaded_at', 'updated_at'
        ]
        read_only_fields = ['id', 'patient', 'file_size_bytes', 'uploaded_at', 'updated_at']

    def validate(self, attrs):
        # Trigger model clean for file validation
        file_obj = attrs.get('file')
        if file_obj:
            instance = MedicalDocument(file=file_obj)
            instance.clean()
        return attrs


class ConsultationNoteSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = ConsultationNote
        fields = [
            'id', 'appointment', 'doctor', 'doctor_name',
            'clinical_observations', 'follow_up_instructions',
            'follow_up_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'doctor', 'created_at', 'updated_at']

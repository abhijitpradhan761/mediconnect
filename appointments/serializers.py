from rest_framework import serializers
from accounts.serializers import UserSerializer
from doctors.serializers import DoctorProfilePublicSerializer
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'doctor_specialization', 'appointment_date', 'start_time', 'end_time',
            'status', 'status_display', 'reason', 'patient_notes', 'doctor_notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'end_time', 'status', 'created_at', 'updated_at']

    def get_patient_name(self, obj):
        return obj.patient.get_full_name() or obj.patient.username

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.get_full_name() or obj.doctor.user.username}"


class AppointmentCreateSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    appointment_date = serializers.DateField()
    slot_time = serializers.TimeField(format='%H:%M', input_formats=['%H:%M'])
    reason = serializers.CharField(required=False, allow_blank=True)

    def validate_appointment_date(self, value):
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Cannot book appointments in the past.")
        return value

    def create(self, validated_data):
        from .services import book_appointment
        from django.core.exceptions import ValidationError as DjValidationError
        try:
            return book_appointment(
                patient_user=self.context['request'].user,
                doctor_profile_id=validated_data['doctor_id'],
                appointment_date=validated_data['appointment_date'],
                slot_time_str=validated_data['slot_time'].strftime('%H:%M'),
                reason=validated_data.get('reason', '')
            )
        except DjValidationError as e:
            raise serializers.ValidationError({'detail': e.message})

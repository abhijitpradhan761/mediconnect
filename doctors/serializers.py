from rest_framework import serializers
from accounts.serializers import UserSerializer
from .models import DoctorProfile, DoctorAvailability


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = DoctorAvailability
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time',
                  'slot_duration_minutes', 'is_active']

    def validate(self, data):
        if data.get('start_time') and data.get('end_time'):
            if data['start_time'] >= data['end_time']:
                raise serializers.ValidationError("End time must be after start time.")
        return data


class DoctorProfilePublicSerializer(serializers.ModelSerializer):
    """Serializer for patient-facing doctor listing — no private data."""
    full_name = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    availabilities = DoctorAvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'full_name', 'email', 'specialization', 'qualification',
            'experience_years', 'consultation_fee', 'bio', 'profile_photo',
            'is_approved', 'availabilities'
        ]

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


class DoctorProfileDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    availabilities = DoctorAvailabilitySerializer(many=True, read_only=True)

    class Meta:
        model = DoctorProfile
        fields = '__all__'

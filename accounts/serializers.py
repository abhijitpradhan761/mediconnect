from rest_framework import serializers
from django.contrib.auth import authenticate
from django.db import transaction
from .models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile


class UserSerializer(serializers.ModelSerializer):
    """
    Standard serializer for user account representation.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_active']
        read_only_fields = ['id', 'role', 'is_active']


class PatientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Patient Profile information.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'date_of_birth', 'gender', 'blood_group',
            'address', 'emergency_contact_name', 'emergency_contact_phone',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class DoctorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Doctor Profile details.
    """
    user = UserSerializer(read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'specialization', 'qualification', 'license_number',
            'experience_years', 'consultation_fee', 'bio', 'is_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_approved', 'created_at', 'updated_at']


class PatientRegisterSerializer(serializers.Serializer):
    """
    Serializer for REST API Patient registration.
    """
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    # Demographics
    date_of_birth = serializers.DateField(required=False, allow_null=True)
    gender = serializers.ChoiceField(choices=PatientProfile.Gender.choices, default=PatientProfile.Gender.MALE)
    blood_group = serializers.ChoiceField(choices=PatientProfile.BloodGroup.choices, required=False, allow_blank=True)
    address = serializers.CharField(required=False, allow_blank=True)
    emergency_contact_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    emergency_contact_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        dob = validated_data.pop('date_of_birth', None)
        gender = validated_data.pop('gender', PatientProfile.Gender.MALE)
        blood_group = validated_data.pop('blood_group', None)
        address = validated_data.pop('address', '')
        emergency_name = validated_data.pop('emergency_contact_name', '')
        emergency_phone = validated_data.pop('emergency_contact_phone', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', ''),
            role=User.Role.PATIENT
        )

        patient_profile = PatientProfile.objects.create(
            user=user,
            date_of_birth=dob,
            gender=gender,
            blood_group=blood_group or None,
            address=address,
            emergency_contact_name=emergency_name,
            emergency_contact_phone=emergency_phone,
        )
        return user


class DoctorRegisterSerializer(serializers.Serializer):
    """
    Serializer for REST API Doctor registration.
    """
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    # Professional details
    specialization = serializers.CharField(max_length=100)
    qualification = serializers.CharField(max_length=150)
    license_number = serializers.CharField(max_length=50)
    experience_years = serializers.IntegerField(min_value=0, default=0)
    consultation_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    bio = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email address already exists.")
        return value

    def validate_license_number(self, value):
        if DoctorProfile.objects.filter(license_number__iexact=value).exists():
            raise serializers.ValidationError("A doctor with this license number is already registered.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password_confirm": "Passwords do not match."})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        specialization = validated_data.pop('specialization')
        qualification = validated_data.pop('qualification')
        license_number = validated_data.pop('license_number')
        experience_years = validated_data.pop('experience_years', 0)
        consultation_fee = validated_data.pop('consultation_fee', 0.00)
        bio = validated_data.pop('bio', '')

        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', ''),
            role=User.Role.DOCTOR
        )

        DoctorProfile.objects.create(
            user=user,
            specialization=specialization,
            qualification=qualification,
            license_number=license_number,
            experience_years=experience_years,
            consultation_fee=consultation_fee,
            bio=bio,
            is_approved=False
        )
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for REST API authentication accepting username or email.
    """
    username_or_email = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username_or_email = attrs.get('username_or_email')
        password = attrs.get('password')

        user = authenticate(username=username_or_email, password=password)
        if not user:
            try:
                user_obj = User.objects.get(email__iexact=username_or_email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None

        if not user:
            raise serializers.ValidationError("Unable to log in with provided credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs['user'] = user
        return attrs

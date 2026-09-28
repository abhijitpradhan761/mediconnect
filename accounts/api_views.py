from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from .serializers import (
    UserSerializer,
    PatientRegisterSerializer,
    DoctorRegisterSerializer,
    LoginSerializer,
    PatientProfileSerializer,
    DoctorProfileSerializer
)
from patients.models import PatientProfile
from doctors.models import DoctorProfile


class RegisterPatientAPIView(APIView):
    """
    POST /api/auth/register/
    Public API endpoint to register a new Patient.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PatientRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = getattr(user, 'patient_profile', None)
            profile_data = PatientProfileSerializer(profile).data if profile else {}
            return Response({
                "message": "Patient registration successful.",
                "user": UserSerializer(user).data,
                "profile": profile_data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterDoctorAPIView(APIView):
    """
    POST /api/auth/register-doctor/
    Public API endpoint to register a Doctor (status defaults to pending approval).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = DoctorRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            profile = getattr(user, 'doctor_profile', None)
            profile_data = DoctorProfileSerializer(profile).data if profile else {}
            return Response({
                "message": "Doctor registration submitted successfully. Awaiting administrator review.",
                "user": UserSerializer(user).data,
                "profile": profile_data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """
    POST /api/auth/login/
    Public API endpoint to authenticate a user via username or email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response({
                "message": "Authentication successful.",
                "user": UserSerializer(user).data,
                "role": user.role
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    POST /api/auth/logout/
    Endpoint to terminate active session.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)


class CurrentUserAPIView(APIView):
    """
    GET /api/auth/user/
    Endpoint to fetch authenticated user information and their associated profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "user": UserSerializer(user).data,
            "role": user.role,
        }
        if user.is_patient and hasattr(user, 'patient_profile'):
            data["patient_profile"] = PatientProfileSerializer(user.patient_profile).data
        elif user.is_doctor and hasattr(user, 'doctor_profile'):
            data["doctor_profile"] = DoctorProfileSerializer(user.doctor_profile).data
        return Response(data, status=status.HTTP_200_OK)

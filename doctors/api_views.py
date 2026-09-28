from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from datetime import date
from accounts.permissions import IsDoctor
from .models import DoctorProfile, DoctorAvailability
from .serializers import DoctorProfilePublicSerializer, DoctorAvailabilitySerializer
from .services import get_available_slots


class DoctorListAPIView(APIView):
    """GET /api/doctors/ — public listing of approved doctors."""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        specialization = request.query_params.get('specialization', '')
        qs = DoctorProfile.objects.filter(is_approved=True).select_related('user')
        if specialization:
            qs = qs.filter(specialization__icontains=specialization)
        serializer = DoctorProfilePublicSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class DoctorDetailAPIView(APIView):
    """GET /api/doctors/<pk>/ — public doctor profile detail."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, pk=pk, is_approved=True)
        serializer = DoctorProfilePublicSerializer(doctor, context={'request': request})
        return Response(serializer.data)


class DoctorAvailabilityAPIView(APIView):
    """GET/POST/PUT/DELETE /api/doctors/<pk>/availability/ — manage doctor's own availability."""
    permission_classes = [permissions.IsAuthenticated, IsDoctor]

    def get(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, pk=pk, user=request.user)
        avails = doctor.availabilities.all()
        return Response(DoctorAvailabilitySerializer(avails, many=True).data)

    def post(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, pk=pk, user=request.user)
        serializer = DoctorAvailabilitySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=doctor)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorSlotsAPIView(APIView):
    """GET /api/doctors/<pk>/slots/?date=YYYY-MM-DD — available time slots."""
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, pk=pk, is_approved=True)
        date_str = request.query_params.get('date', '')
        if not date_str:
            return Response({'error': 'date parameter required (YYYY-MM-DD).'}, status=400)
        try:
            target_date = date.fromisoformat(date_str)
        except ValueError:
            return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

        if target_date < date.today():
            return Response({'error': 'Cannot query slots for past dates.'}, status=400)

        slots = get_available_slots(doctor, target_date)
        return Response({'date': date_str, 'doctor_id': pk, 'slots': slots})

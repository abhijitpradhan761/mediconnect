from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError as DjValidationError
from accounts.permissions import IsPatient
from .models import Appointment
from .serializers import AppointmentSerializer, AppointmentCreateSerializer
from .services import cancel_appointment


class AppointmentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_patient:
            qs = Appointment.objects.filter(patient=user)
        elif user.is_doctor:
            qs = Appointment.objects.filter(doctor__user=user)
        else:
            qs = Appointment.objects.all()
        serializer = AppointmentSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_patient:
            return Response({'detail': 'Only patients can book appointments.'}, status=403)
        serializer = AppointmentCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            appt = serializer.save()
            return Response(AppointmentSerializer(appt).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppointmentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def _get_appointment(self, pk, user):
        appt = get_object_or_404(Appointment, pk=pk)
        if user.is_patient and appt.patient != user:
            return None
        if user.is_doctor and appt.doctor.user != user:
            return None
        return appt

    def get(self, request, pk):
        appt = self._get_appointment(pk, request.user)
        if not appt:
            return Response({'detail': 'Not found.'}, status=404)
        return Response(AppointmentSerializer(appt).data)


class AppointmentCancelAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            appt = cancel_appointment(pk, request.user)
            return Response({'detail': 'Appointment cancelled.', 'status': appt.status})
        except DjValidationError as e:
            return Response({'detail': str(e.message if hasattr(e, 'message') else e)}, status=400)

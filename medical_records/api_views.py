from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import MedicalDocument, ConsultationNote
from .serializers import MedicalDocumentSerializer, ConsultationNoteSerializer
from appointments.models import Appointment
from doctors.models import DoctorProfile


class MedicalDocumentAPIView(APIView):
    """
    GET /api/medical-records/ - list user's documents
    POST /api/medical-records/ - upload document (Patient only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_patient:
            qs = MedicalDocument.objects.filter(patient=user)
        elif user.is_doctor:
            patient_ids = Appointment.objects.filter(
                doctor__user=user,
                status__in=['CONFIRMED', 'COMPLETED']
            ).values_list('patient_id', flat=True).distinct()
            qs = MedicalDocument.objects.filter(patient_id__in=patient_ids)
        elif user.is_administrator:
            qs = MedicalDocument.objects.all()
        else:
            qs = MedicalDocument.objects.none()

        serializer = MedicalDocumentSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_patient:
            return Response({'detail': 'Only patients can upload medical documents.'}, status=403)

        serializer = MedicalDocumentSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            doc = serializer.save(patient=request.user)
            return Response(MedicalDocumentSerializer(doc).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MedicalDocumentDetailAPIView(APIView):
    """
    GET /api/medical-records/<pk>/ - view document metadata
    DELETE /api/medical-records/<pk>/ - delete document (Owner only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def _get_doc_or_403(self, pk, user):
        doc = get_object_or_404(MedicalDocument, pk=pk)
        is_owner = (doc.patient == user)
        is_attending_doctor = (
            user.is_doctor and
            Appointment.objects.filter(
                doctor__user=user,
                patient=doc.patient,
                status__in=['CONFIRMED', 'COMPLETED']
            ).exists()
        )
        if not (is_owner or is_attending_doctor or user.is_administrator):
            return None, False
        return doc, is_owner

    def get(self, request, pk):
        doc, _ = self._get_doc_or_403(pk, request.user)
        if doc is None:
            return Response({'detail': 'Access denied to this document.'}, status=403)
        return Response(MedicalDocumentSerializer(doc).data)

    def delete(self, request, pk):
        doc, is_owner = self._get_doc_or_403(pk, request.user)
        if doc is None or not (is_owner or request.user.is_administrator):
            return Response({'detail': 'You can only delete your own documents.'}, status=403)
        doc.delete()
        return Response({'detail': 'Document deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


class ConsultationNoteAPIView(APIView):
    """
    GET /api/notes/?appointment_id=<id>
    POST /api/notes/ (Doctor only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        appt_id = request.query_params.get('appointment_id')
        if not appt_id:
            return Response({'detail': 'appointment_id query param is required.'}, status=400)

        note = get_object_or_404(ConsultationNote, appointment_id=appt_id)
        user = request.user
        if not (note.appointment.patient == user or note.doctor.user == user or user.is_administrator):
            return Response({'detail': 'Access denied.'}, status=403)

        return Response(ConsultationNoteSerializer(note).data)

    def post(self, request):
        if not request.user.is_doctor:
            return Response({'detail': 'Only doctors can create consultation notes.'}, status=403)

        profile = get_object_or_404(DoctorProfile, user=request.user)
        serializer = ConsultationNoteSerializer(data=request.data)
        if serializer.is_valid():
            appt = serializer.validated_data['appointment']
            if appt.doctor != profile:
                return Response({'detail': 'You can only write notes for your own appointments.'}, status=403)
            note = serializer.save(doctor=profile)
            return Response(ConsultationNoteSerializer(note).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

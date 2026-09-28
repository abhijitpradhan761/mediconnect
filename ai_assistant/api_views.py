from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.permissions import IsPatient
from .serializers import (
    SymptomOrganizerSerializer,
    QuestionGeneratorSerializer,
    DocumentSummarizerSerializer
)
from .services import organize_symptoms, generate_doctor_questions, summarize_medical_document


class SymptomSummaryAPIView(APIView):
    """
    POST /api/ai/symptom-summary/
    Organizes patient symptoms for clinical review.
    """
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def post(self, request):
        serializer = SymptomOrganizerSerializer(data=request.data)
        if serializer.is_valid():
            summary = organize_symptoms(
                symptoms=serializer.validated_data['symptoms'],
                duration=serializer.validated_data['duration'],
                severity=str(serializer.validated_data['severity']),
                context=serializer.validated_data.get('context', '')
            )
            return Response({
                'symptom_summary': summary,
                'disclaimer': 'For preparation and discussion only. Not a medical diagnosis.'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DoctorQuestionsAPIView(APIView):
    """
    POST /api/ai/questions/
    Generates empowered questions to ask the doctor.
    """
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def post(self, request):
        serializer = QuestionGeneratorSerializer(data=request.data)
        if serializer.is_valid():
            questions = generate_doctor_questions(
                symptoms=serializer.validated_data['symptoms'],
                appointment_reason=serializer.validated_data.get('appointment_reason', '')
            )
            return Response({
                'suggested_questions': questions,
                'disclaimer': 'For preparation and discussion only. Not a medical diagnosis.'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentSummaryAPIView(APIView):
    """
    POST /api/ai/summarize-document/
    Provides plain-language explanations of medical reports.
    """
    permission_classes = [permissions.IsAuthenticated, IsPatient]

    def post(self, request):
        serializer = DocumentSummarizerSerializer(data=request.data)
        if serializer.is_valid():
            summary = summarize_medical_document(
                document_text=serializer.validated_data['document_text']
            )
            return Response({
                'document_summary': summary,
                'disclaimer': 'For preparation and discussion only. Not a medical diagnosis.'
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

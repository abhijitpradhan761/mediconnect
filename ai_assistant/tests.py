from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from ai_assistant.services import (
    organize_symptoms,
    generate_doctor_questions,
    summarize_medical_document,
    AI_DISCLAIMER
)

User = get_user_model()


class ResponsibleAIAssistantTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()

        self.patient = User.objects.create_user(
            username='patient_chloe',
            email='chloe@example.com',
            password='Password123!',
            role=User.Role.PATIENT
        )

        self.doctor = User.objects.create_user(
            username='dr_strange',
            email='strange@clinic.org',
            password='Password123!',
            role=User.Role.DOCTOR
        )

    def test_symptom_organizer_includes_mandatory_medical_disclaimer(self):
        summary = organize_symptoms(
            symptoms='Frontal headache and nausea',
            duration='3 days',
            severity='6',
            context='Worse under fluorescent lighting'
        )
        self.assertIn('Medical Notice', summary)
        self.assertIn('not a medical diagnosis', summary.lower())

    def test_question_generator_service(self):
        questions = generate_doctor_questions(
            symptoms='Persistent shoulder stiffness',
            appointment_reason='Physical Therapy Consultation'
        )
        self.assertIsNotNone(questions)
        self.assertIn('Medical Notice', questions)

    def test_document_summarizer_rejects_empty_text(self):
        result = summarize_medical_document("Short")
        self.assertIn('more detailed document text', result)

    def test_api_symptom_summary_endpoint(self):
        self.api_client.force_authenticate(user=self.patient)
        response = self.api_client.post(reverse('api_ai_symptom_summary'), {
            'symptoms': 'Dry cough and mild throat irritation',
            'duration': '4 days',
            'severity': 4,
            'context': 'No fever reported'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('symptom_summary', response.data)
        self.assertIn('disclaimer', response.data)

    def test_api_requires_patient_role(self):
        # Doctor role should not access patient symptom organizer API
        self.api_client.force_authenticate(user=self.doctor)
        response = self.api_client.post(reverse('api_ai_symptom_summary'), {
            'symptoms': 'Headache',
            'duration': '1 day',
            'severity': 3
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

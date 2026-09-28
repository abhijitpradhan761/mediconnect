from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from datetime import date, time
from medical_records.models import MedicalDocument, ConsultationNote
from appointments.models import Appointment
from doctors.models import DoctorProfile

User = get_user_model()


class MedicalRecordsAndSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.patient = User.objects.create_user(
            username='patient_david',
            email='david@example.com',
            password='Password123!',
            role=User.Role.PATIENT
        )

        self.stranger = User.objects.create_user(
            username='stranger_dan',
            email='dan@example.com',
            password='Password123!',
            role=User.Role.PATIENT
        )

        self.doctor_user = User.objects.create_user(
            username='dr_foster',
            email='foster@hospital.org',
            password='Password123!',
            role=User.Role.DOCTOR
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Dermatology',
            qualification='MD',
            license_number='DERM-404',
            is_approved=True
        )

        # Upload a test document for patient
        self.sample_file = SimpleUploadedFile(
            "lab_report.pdf",
            b"Dummy PDF content for medical lab results.",
            content_type="application/pdf"
        )
        self.document = MedicalDocument.objects.create(
            patient=self.patient,
            title='Annual Blood Test',
            document_type=MedicalDocument.DocumentType.LAB_REPORT,
            file=self.sample_file
        )

    def test_document_creation_and_metadata(self):
        self.assertEqual(self.document.title, 'Annual Blood Test')
        self.assertEqual(self.document.patient, self.patient)
        self.assertGreater(self.document.file_size_bytes, 0)

    def test_invalid_file_extension_rejected(self):
        bad_file = SimpleUploadedFile(
            "malicious.exe",
            b"Binary content here",
            content_type="application/octet-stream"
        )
        doc = MedicalDocument(
            patient=self.patient,
            title='Executable test',
            file=bad_file
        )
        with self.assertRaises(ValidationError):
            doc.clean()

    def test_document_owner_can_access_detail(self):
        self.client.login(username='patient_david', password='Password123!')
        response = self.client.get(reverse('document_detail', kwargs={'pk': self.document.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annual Blood Test')

    def test_unrelated_patient_cannot_access_private_document(self):
        self.client.login(username='stranger_dan', password='Password123!')
        response = self.client.get(reverse('document_detail', kwargs={'pk': self.document.pk}))
        self.assertEqual(response.status_code, 403)

    def test_attending_doctor_can_access_patient_document(self):
        # Create a confirmed appointment connecting doctor_foster and patient_david
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor_profile,
            appointment_date=date.today(),
            start_time=time(10, 0),
            end_time=time(10, 30),
            status=Appointment.Status.CONFIRMED,
            reason='Skin exam'
        )

        self.client.login(username='dr_foster', password='Password123!')
        response = self.client.get(reverse('document_detail', kwargs={'pk': self.document.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Annual Blood Test')

    def test_doctor_can_record_consultation_notes(self):
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor_profile,
            appointment_date=date.today(),
            start_time=time(14, 0),
            end_time=time(14, 30),
            status=Appointment.Status.CONFIRMED
        )

        note = ConsultationNote.objects.create(
            appointment=appt,
            doctor=self.doctor_profile,
            clinical_observations='Mild eczema on right forearm. Recommended topical moisturizer.',
            follow_up_instructions='Apply twice daily. Follow up in 3 weeks if no improvement.'
        )
        self.assertIsNotNone(note.pk)
        self.assertEqual(note.appointment, appt)

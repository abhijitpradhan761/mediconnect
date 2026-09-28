from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from doctors.models import DoctorProfile
from patients.models import PatientProfile
from appointments.models import Appointment

User = get_user_model()


class AdminDashboardAndReportsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()

        self.admin = User.objects.create_superuser(
            username='admin_chief',
            email='chief@mediconnect.org',
            password='Password123!',
            role=User.Role.ADMIN
        )

        self.patient = User.objects.create_user(
            username='patient_ron',
            email='ron@example.com',
            password='Password123!',
            role=User.Role.PATIENT
        )
        PatientProfile.objects.create(user=self.patient)

        self.doctor_user = User.objects.create_user(
            username='dr_clara',
            email='clara@hospital.org',
            password='Password123!',
            role=User.Role.DOCTOR
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Cardiology',
            qualification='MD',
            license_number='CARD-555',
            is_approved=False
        )

    def test_admin_dashboard_renders_stats(self):
        self.client.login(username='admin_chief', password='Password123!')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Platform Overview')
        self.assertContains(response, 'Registered Patients')

    def test_admin_doctor_approval_workflow(self):
        self.client.login(username='admin_chief', password='Password123!')
        self.assertFalse(self.doctor_profile.is_approved)

        # Approve doctor
        approve_resp = self.client.post(reverse('admin_approve_doctor', kwargs={'pk': self.doctor_profile.pk}))
        self.assertEqual(approve_resp.status_code, 302)

        self.doctor_profile.refresh_from_db()
        self.assertTrue(self.doctor_profile.is_approved)

        # Revoke approval
        revoke_resp = self.client.post(reverse('admin_revoke_doctor', kwargs={'pk': self.doctor_profile.pk}))
        self.assertEqual(revoke_resp.status_code, 302)

        self.doctor_profile.refresh_from_db()
        self.assertFalse(self.doctor_profile.is_approved)

    def test_admin_toggle_user_active_state(self):
        self.client.login(username='admin_chief', password='Password123!')
        self.assertTrue(self.patient.is_active)

        # Deactivate
        self.client.post(reverse('admin_toggle_user_active', kwargs={'user_id': self.patient.pk}))
        self.patient.refresh_from_db()
        self.assertFalse(self.patient.is_active)

        # Reactivate
        self.client.post(reverse('admin_toggle_user_active', kwargs={'user_id': self.patient.pk}))
        self.patient.refresh_from_db()
        self.assertTrue(self.patient.is_active)

    def test_admin_reports_view_renders_charts(self):
        self.client.login(username='admin_chief', password='Password123!')
        response = self.client.get(reverse('admin_reports'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Operational Analytics')

    def test_api_admin_dashboard_stats(self):
        self.api_client.force_authenticate(user=self.admin)
        response = self.api_client.get(reverse('api_admin_dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_patients', response.data)
        self.assertIn('total_doctors', response.data)
        self.assertIn('total_appointments', response.data)

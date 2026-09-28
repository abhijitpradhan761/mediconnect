from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from patients.models import PatientProfile
from doctors.models import DoctorProfile

User = get_user_model()


class AuthenticationAndRBACTests(TestCase):
    """
    Test suite for Accounts authentication, registration, and RBAC permissions.
    """
    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()

        # Create demo accounts
        self.patient_user = User.objects.create_user(
            username='patient_alice',
            email='alice@example.com',
            password='Password123!',
            first_name='Alice',
            last_name='Walker',
            role=User.Role.PATIENT,
        )
        self.patient_profile = PatientProfile.objects.create(
            user=self.patient_user,
            gender=PatientProfile.Gender.FEMALE,
            blood_group=PatientProfile.BloodGroup.O_POS
        )

        self.doctor_user = User.objects.create_user(
            username='dr_smith',
            email='smith@hospital.org',
            password='Password123!',
            first_name='John',
            last_name='Smith',
            role=User.Role.DOCTOR,
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Cardiology',
            qualification='MBBS, MD',
            license_number='MED-12345',
            is_approved=True
        )

        self.admin_user = User.objects.create_superuser(
            username='admin_boss',
            email='admin@mediconnect.org',
            password='Password123!',
            role=User.Role.ADMIN
        )

    def test_home_page_renders_with_disclaimer(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MediConnect')
        self.assertContains(response, 'Medical Disclaimer')

    def test_patient_registration_web_view(self):
        response = self.client.post(reverse('patient_register'), {
            'first_name': 'Bob',
            'last_name': 'Taylor',
            'username': 'bob_patient',
            'email': 'bob@example.com',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'gender': 'MALE',
            'blood_group': 'A+',
            'phone_number': '+1-555-0988',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='bob_patient').exists())
        new_user = User.objects.get(username='bob_patient')
        self.assertEqual(new_user.role, User.Role.PATIENT)
        self.assertTrue(hasattr(new_user, 'patient_profile'))

    def test_doctor_registration_starts_as_unapproved(self):
        response = self.client.post(reverse('doctor_register'), {
            'first_name': 'Sarah',
            'last_name': 'Connor',
            'username': 'dr_sarah',
            'email': 'sarah@clinic.org',
            'password': 'Password123!',
            'confirm_password': 'Password123!',
            'specialization': 'Neurology',
            'qualification': 'MD, PhD',
            'license_number=': 'NEURO-999',
            'license_number': 'NEURO-999',
            'experience_years': 8,
            'consultation_fee': '75.00',
        })
        self.assertEqual(response.status_code, 302)
        new_doc = User.objects.get(username='dr_sarah')
        self.assertEqual(new_doc.role, User.Role.DOCTOR)
        self.assertFalse(new_doc.doctor_profile.is_approved)

    def test_login_with_username_and_email(self):
        # Login with username
        logged_in = self.client.login(username='patient_alice', password='Password123!')
        self.assertTrue(logged_in)
        self.client.logout()

        # Login with email
        logged_in_email = self.client.post(reverse('login'), {
            'username_or_email': 'alice@example.com',
            'password': 'Password123!'
        })
        self.assertEqual(logged_in_email.status_code, 302)

    def test_invalid_login_rejected(self):
        response = self.client.post(reverse('login'), {
            'username_or_email': 'patient_alice',
            'password': 'WrongPassword999!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid login credentials')

    def test_rbac_access_restrictions(self):
        # Patient trying to access doctor dashboard gets 403 Forbidden
        self.client.login(username='patient_alice', password='Password123!')
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 403)

        # Patient trying to access admin dashboard gets 403 Forbidden
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

        # Doctor trying to access patient dashboard gets 403 Forbidden
        self.client.login(username='dr_smith', password='Password123!')
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 403)
        self.client.logout()

    def test_api_auth_login_and_user_endpoint(self):
        # API Login
        login_resp = self.api_client.post(reverse('api_login'), {
            'username_or_email': 'patient_alice',
            'password': 'Password123!'
        })
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(login_resp.data['role'], 'PATIENT')

        # Current User API
        user_resp = self.api_client.get(reverse('api_current_user'))
        self.assertEqual(user_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(user_resp.data['user']['username'], 'patient_alice')

        # API Logout
        logout_resp = self.api_client.post(reverse('api_logout'))
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)

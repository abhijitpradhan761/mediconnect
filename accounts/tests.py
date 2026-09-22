from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class FoundationAndUserRoleTests(TestCase):
    """
    Test suite for Phase 1: Project Foundation & Custom User Model.
    """

    def setUp(self):
        self.client = Client()

    def test_home_page_renders_successfully(self):
        """Verify that the home page returns HTTP 200 and displays MediConnect branding."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'MediConnect')
        self.assertContains(response, 'Medical Disclaimer')

    def test_user_creation_with_patient_role(self):
        """Verify patient user creation and role property methods."""
        patient_user = User.objects.create_user(
            username='john_patient',
            email='john@example.com',
            password='SecurePassword123!',
            role=User.Role.PATIENT,
            phone_number='+1-555-0199',
        )
        self.assertEqual(patient_user.role, 'PATIENT')
        self.assertTrue(patient_user.is_patient)
        self.assertFalse(patient_user.is_doctor)
        self.assertFalse(patient_user.is_administrator)

    def test_user_creation_with_doctor_role(self):
        """Verify doctor user creation and role property methods."""
        doctor_user = User.objects.create_user(
            username='dr_smith',
            email='smith@mediconnect.org',
            password='SecurePassword123!',
            role=User.Role.DOCTOR,
            phone_number='+1-555-0144',
        )
        self.assertEqual(doctor_user.role, 'DOCTOR')
        self.assertFalse(doctor_user.is_patient)
        self.assertTrue(doctor_user.is_doctor)
        self.assertFalse(doctor_user.is_administrator)

    def test_user_creation_with_admin_role(self):
        """Verify administrator user creation and role property methods."""
        admin_user = User.objects.create_superuser(
            username='admin_boss',
            email='admin@mediconnect.org',
            password='SecurePassword123!',
            role=User.Role.ADMIN,
        )
        self.assertEqual(admin_user.role, 'ADMIN')
        self.assertFalse(admin_user.is_patient)
        self.assertFalse(admin_user.is_doctor)
        self.assertTrue(admin_user.is_administrator)

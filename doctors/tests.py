from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import time, date, timedelta
from rest_framework import status
from rest_framework.test import APIClient
from doctors.models import DoctorProfile, DoctorAvailability
from doctors.services import get_available_slots

User = get_user_model()


class DoctorAndAvailabilityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()

        self.doctor_user = User.objects.create_user(
            username='dr_watson',
            email='watson@clinic.org',
            password='Password123!',
            first_name='John',
            last_name='Watson',
            role=User.Role.DOCTOR
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Pulmonology',
            qualification='MBBS, FCCP',
            license_number='PULM-777',
            consultation_fee='80.00',
            is_approved=True
        )

        # Set availability for Monday (0) 09:00 - 11:00 with 30 min slots
        self.avail = DoctorAvailability.objects.create(
            doctor=self.doctor_profile,
            day_of_week=0,  # Monday
            start_time=time(9, 0),
            end_time=time(11, 0),
            slot_duration_minutes=30,
            is_active=True
        )

    def test_doctor_list_view_and_filtering(self):
        response = self.client.get(reverse('doctor_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. John Watson')
        self.assertContains(response, 'Pulmonology')

        # Filter by specialization
        filter_resp = self.client.get(reverse('doctor_list') + '?specialization=Pulmonology')
        self.assertEqual(filter_resp.status_code, 200)
        self.assertContains(filter_resp, 'Dr. John Watson')

    def test_slot_generation_service(self):
        # Find next Monday
        today = date.today()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)

        slots = get_available_slots(self.doctor_profile, next_monday)
        self.assertEqual(len(slots), 4)  # 09:00, 09:30, 10:00, 10:30
        self.assertEqual(slots[0]['time'], '09:00')
        self.assertTrue(slots[0]['available'])
        self.assertEqual(slots[3]['time'], '10:30')

    def test_api_doctor_slots_endpoint(self):
        today = date.today()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        next_monday = today + timedelta(days=days_ahead)

        url = reverse('api_doctor_slots', kwargs={'pk': self.doctor_profile.pk})
        response = self.api_client.get(f"{url}?date={next_monday.isoformat()}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('slots', response.data)
        self.assertEqual(len(response.data['slots']), 4)

    def test_api_doctor_slots_past_date_rejected(self):
        url = reverse('api_doctor_slots', kwargs={'pk': self.doctor_profile.pk})
        past_date = date.today() - timedelta(days=5)
        response = self.api_client.get(f"{url}?date={past_date.isoformat()}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

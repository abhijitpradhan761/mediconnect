from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from datetime import time, date, timedelta
from appointments.models import Appointment
from appointments.services import book_appointment, cancel_appointment
from doctors.models import DoctorProfile, DoctorAvailability

User = get_user_model()


class AppointmentEngineTests(TestCase):
    def setUp(self):
        self.client = Client()

        self.patient = User.objects.create_user(
            username='patient_mark',
            email='mark@example.com',
            password='Password123!',
            first_name='Mark',
            role=User.Role.PATIENT
        )

        self.other_patient = User.objects.create_user(
            username='patient_lucy',
            email='lucy@example.com',
            password='Password123!',
            first_name='Lucy',
            role=User.Role.PATIENT
        )

        self.doctor_user = User.objects.create_user(
            username='dr_house',
            email='house@clinic.org',
            password='Password123!',
            first_name='Gregory',
            last_name='House',
            role=User.Role.DOCTOR
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Diagnostic Medicine',
            qualification='MD',
            license_number='DIAG-101',
            is_approved=True
        )

        # Tuesday (1) availability: 10:00 - 12:00 (4 slots: 10:00, 10:30, 11:00, 11:30)
        self.avail = DoctorAvailability.objects.create(
            doctor=self.doctor_profile,
            day_of_week=1,
            start_time=time(10, 0),
            end_time=time(12, 0),
            slot_duration_minutes=30,
            is_active=True
        )

        # Target next Tuesday
        today = date.today()
        days_ahead = 1 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        self.next_tuesday = today + timedelta(days=days_ahead)

    def test_successful_appointment_booking(self):
        appt = book_appointment(
            patient_user=self.patient,
            doctor_profile_id=self.doctor_profile.pk,
            appointment_date=self.next_tuesday,
            slot_time_str='10:00',
            reason='Routine clinical review'
        )
        self.assertIsNotNone(appt.pk)
        self.assertEqual(appt.status, Appointment.Status.PENDING)
        self.assertEqual(appt.start_time, time(10, 0))
        self.assertEqual(appt.end_time, time(10, 30))

    def test_double_booking_prevention(self):
        # First booking succeeds
        book_appointment(
            patient_user=self.patient,
            doctor_profile_id=self.doctor_profile.pk,
            appointment_date=self.next_tuesday,
            slot_time_str='10:30',
            reason='First booking'
        )

        # Second patient attempting same doctor, same date, same slot must raise ValidationError
        with self.assertRaises(ValidationError):
            book_appointment(
                patient_user=self.other_patient,
                doctor_profile_id=self.doctor_profile.pk,
                appointment_date=self.next_tuesday,
                slot_time_str='10:30',
                reason='Duplicate booking attempt'
            )

    def test_past_date_booking_rejected(self):
        past_date = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            book_appointment(
                patient_user=self.patient,
                doctor_profile_id=self.doctor_profile.pk,
                appointment_date=past_date,
                slot_time_str='10:00',
                reason='Past visit'
            )

    def test_appointment_cancellation(self):
        appt = book_appointment(
            patient_user=self.patient,
            doctor_profile_id=self.doctor_profile.pk,
            appointment_date=self.next_tuesday,
            slot_time_str='11:00',
            reason='To be cancelled'
        )
        cancelled = cancel_appointment(appt.pk, self.patient)
        self.assertEqual(cancelled.status, Appointment.Status.CANCELLED)

    def test_unauthorized_user_cannot_cancel_appointment(self):
        appt = book_appointment(
            patient_user=self.patient,
            doctor_profile_id=self.doctor_profile.pk,
            appointment_date=self.next_tuesday,
            slot_time_str='11:30',
            reason='Private visit'
        )
        with self.assertRaises(ValidationError):
            cancel_appointment(appt.pk, self.other_patient)

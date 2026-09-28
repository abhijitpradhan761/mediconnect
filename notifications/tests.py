from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from notifications.models import Notification
from notifications.services import (
    create_notification,
    notify_appointment_booked,
    notify_appointment_status_changed
)
from doctors.models import DoctorProfile
from appointments.models import Appointment
from datetime import date, time

User = get_user_model()


class NotificationSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.api_client = APIClient()

        self.patient = User.objects.create_user(
            username='patient_emma',
            email='emma@example.com',
            password='Password123!',
            first_name='Emma',
            role=User.Role.PATIENT
        )

        self.doctor_user = User.objects.create_user(
            username='dr_chen',
            email='chen@clinic.org',
            password='Password123!',
            first_name='Li',
            last_name='Chen',
            role=User.Role.DOCTOR
        )
        self.doctor_profile = DoctorProfile.objects.create(
            user=self.doctor_user,
            specialization='Pediatrics',
            qualification='MD',
            license_number='PED-888',
            is_approved=True
        )

    def test_notification_creation_and_unread_count(self):
        create_notification(
            recipient=self.patient,
            notification_type=Notification.NotificationType.GENERAL,
            title='Welcome to MediConnect',
            message='Your account has been setup successfully.'
        )

        self.api_client.force_authenticate(user=self.patient)
        response = self.api_client.get(reverse('api_unread_count'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['unread_count'], 1)

    def test_mark_notification_as_read(self):
        notif = create_notification(
            recipient=self.patient,
            notification_type=Notification.NotificationType.APPOINTMENT_CONFIRMED,
            title='Confirmed Visit',
            message='Your appointment is confirmed.'
        )
        self.assertFalse(notif.is_read)

        self.client.login(username='patient_emma', password='Password123!')
        response = self.client.post(reverse('mark_notification_read', kwargs={'pk': notif.pk}))
        self.assertEqual(response.status_code, 302)

        notif.refresh_from_db()
        self.assertTrue(notif.is_read)

    def test_appointment_booking_triggers_notifications(self):
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor_profile,
            appointment_date=date.today(),
            start_time=time(9, 0),
            end_time=time(9, 30),
            status=Appointment.Status.PENDING
        )
        notify_appointment_booked(appt)

        # Both patient and doctor should receive notification
        self.assertTrue(Notification.objects.filter(recipient=self.patient).exists())
        self.assertTrue(Notification.objects.filter(recipient=self.doctor_user).exists())

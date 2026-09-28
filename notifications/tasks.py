from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@shared_task(name='notifications.send_appointment_reminder')
def send_appointment_reminder(appointment_id: int):
    """
    Celery task: sends an in-app reminder notification 24h prior to appointment.
    """
    from appointments.models import Appointment
    from .services import create_notification, Notification

    try:
        appointment = Appointment.objects.select_related('patient', 'doctor__user').get(pk=appointment_id)
    except Appointment.DoesNotExist:
        logger.warning(f"Reminder skipped: Appointment {appointment_id} does not exist.")
        return f"Appointment {appointment_id} not found."

    if appointment.status not in ['PENDING', 'CONFIRMED']:
        return f"Skipped: Appointment {appointment_id} is in status '{appointment.status}'."

    create_notification(
        recipient=appointment.patient,
        notification_type=Notification.NotificationType.APPOINTMENT_REMINDER,
        title="Upcoming Appointment Reminder",
        message=f"Reminder: You have an appointment tomorrow, {appointment.appointment_date} at {appointment.start_time.strftime('%H:%M')} with Dr. {appointment.doctor.user.get_full_name()}.",
        related_appointment_id=appointment.pk,
    )
    return f"Reminder sent for appointment {appointment_id}."


@shared_task(name='notifications.schedule_reminders_for_tomorrow')
def schedule_reminders_for_tomorrow():
    """
    Periodic Celery Beat task: Scans for all upcoming appointments for tomorrow
    and dispatches individual reminder tasks.
    """
    from appointments.models import Appointment

    tomorrow = timezone.now().date() + timedelta(days=1)
    upcoming_appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        status__in=['PENDING', 'CONFIRMED']
    )

    count = 0
    for appt in upcoming_appointments:
        send_appointment_reminder.delay(appt.pk)
        count += 1

    return f"Scheduled {count} appointment reminders for {tomorrow}."


@shared_task(name='notifications.async_notify_doctor_approved')
def async_notify_doctor_approved(doctor_profile_id: int):
    """
    Asynchronous notification when a doctor is approved by administrator.
    """
    from doctors.models import DoctorProfile
    from .services import notify_doctor_approved

    try:
        profile = DoctorProfile.objects.select_related('user').get(pk=doctor_profile_id)
        notify_doctor_approved(profile)
        return f"Approval notification delivered to Dr. {profile.user.username}."
    except DoctorProfile.DoesNotExist:
        return f"DoctorProfile {doctor_profile_id} not found."

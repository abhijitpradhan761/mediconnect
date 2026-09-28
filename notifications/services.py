from .models import Notification


def create_notification(recipient, notification_type, title, message, related_appointment_id=None):
    """
    Creates an in-app notification record.
    """
    return Notification.objects.create(
        recipient=recipient,
        notification_type=notification_type,
        title=title,
        message=message,
        related_appointment_id=related_appointment_id,
    )


def notify_appointment_booked(appointment):
    """
    Notifies both doctor and patient upon initial booking.
    """
    # Notify doctor
    create_notification(
        recipient=appointment.doctor.user,
        notification_type=Notification.NotificationType.APPOINTMENT_BOOKED,
        title="New Appointment Request",
        message=f"Patient {appointment.patient.get_full_name() or appointment.patient.username} has requested an appointment on {appointment.appointment_date} at {appointment.start_time.strftime('%H:%M')}.",
        related_appointment_id=appointment.pk,
    )
    # Notify patient
    create_notification(
        recipient=appointment.patient,
        notification_type=Notification.NotificationType.APPOINTMENT_BOOKED,
        title="Appointment Request Submitted",
        message=f"Your appointment request with Dr. {appointment.doctor.user.get_full_name()} on {appointment.appointment_date} at {appointment.start_time.strftime('%H:%M')} is pending doctor confirmation.",
        related_appointment_id=appointment.pk,
    )


def notify_appointment_status_changed(appointment):
    """
    Sends notification when appointment status transitions.
    """
    status_map = {
        'CONFIRMED': (
            Notification.NotificationType.APPOINTMENT_CONFIRMED,
            "Appointment Confirmed",
            f"Dr. {appointment.doctor.user.get_full_name()} has confirmed your consultation for {appointment.appointment_date} at {appointment.start_time.strftime('%H:%M')}."
        ),
        'REJECTED': (
            Notification.NotificationType.APPOINTMENT_REJECTED,
            "Appointment Request Declined",
            f"Dr. {appointment.doctor.user.get_full_name()} was unable to accept your appointment for {appointment.appointment_date}."
        ),
        'COMPLETED': (
            Notification.NotificationType.APPOINTMENT_COMPLETED,
            "Consultation Completed",
            f"Your appointment with Dr. {appointment.doctor.user.get_full_name()} on {appointment.appointment_date} has been marked completed. You can view consultation notes in your portal."
        ),
        'CANCELLED': (
            Notification.NotificationType.APPOINTMENT_CANCELLED,
            "Appointment Cancelled",
            f"The appointment on {appointment.appointment_date} at {appointment.start_time.strftime('%H:%M')} has been cancelled."
        ),
    }

    if appointment.status in status_map:
        notif_type, title, msg = status_map[appointment.status]
        create_notification(
            recipient=appointment.patient,
            notification_type=notif_type,
            title=title,
            message=msg,
            related_appointment_id=appointment.pk,
        )


def notify_doctor_approved(doctor_profile):
    """
    Notifies a doctor that their license and account have been approved.
    """
    create_notification(
        recipient=doctor_profile.user,
        notification_type=Notification.NotificationType.DOCTOR_APPROVED,
        title="MediConnect Credentials Approved!",
        message="Congratulations! Your medical qualifications have been verified by an administrator. Your profile is now public and open for patient bookings.",
    )

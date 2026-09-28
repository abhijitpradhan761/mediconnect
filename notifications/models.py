from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    In-app notifications for appointment status changes, reminders,
    document uploads, and account verification updates.
    """
    class NotificationType(models.TextChoices):
        APPOINTMENT_BOOKED = 'APPOINTMENT_BOOKED', 'Appointment Booked'
        APPOINTMENT_CONFIRMED = 'APPOINTMENT_CONFIRMED', 'Appointment Confirmed'
        APPOINTMENT_CANCELLED = 'APPOINTMENT_CANCELLED', 'Appointment Cancelled'
        APPOINTMENT_REJECTED = 'APPOINTMENT_REJECTED', 'Appointment Rejected'
        APPOINTMENT_COMPLETED = 'APPOINTMENT_COMPLETED', 'Appointment Completed'
        APPOINTMENT_REMINDER = 'APPOINTMENT_REMINDER', 'Appointment Reminder'
        DOCTOR_APPROVED = 'DOCTOR_APPROVED', 'Doctor Approved'
        DOCUMENT_UPLOADED = 'DOCUMENT_UPLOADED', 'Document Uploaded'
        GENERAL = 'GENERAL', 'General Information'

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='Recipient user of this notification.'
    )
    notification_type = models.CharField(
        max_length=40,
        choices=NotificationType.choices,
        default=NotificationType.GENERAL
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    related_appointment_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"[{self.get_notification_type_display()}] -> {self.recipient.username}: {self.title}"

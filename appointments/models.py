from django.db import models
from django.conf import settings


class Appointment(models.Model):
    """
    Core appointment record linking a patient to a doctor on a specific date and time slot.
    Database-level unique constraint prevents double booking of the same slot.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'
        REJECTED = 'REJECTED', 'Rejected'

    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_appointments',
        limit_choices_to={'role': 'PATIENT'}
    )
    doctor = models.ForeignKey(
        'doctors.DoctorProfile',
        on_delete=models.CASCADE,
        related_name='doctor_appointments'
    )
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    reason = models.TextField(blank=True, help_text='Reason for the visit.')
    patient_notes = models.TextField(blank=True)
    doctor_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-start_time']
        # Database-level constraint prevents double booking of same doctor+date+slot
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'start_time'],
                condition=models.Q(status__in=['PENDING', 'CONFIRMED']),
                name='unique_active_doctor_slot'
            )
        ]

    def __str__(self):
        return (
            f"{self.patient.get_full_name()} ↔ Dr.{self.doctor.user.get_full_name()} "
            f"on {self.appointment_date} at {self.start_time}"
        )

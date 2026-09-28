from django.db import models
from django.conf import settings


class DoctorProfile(models.Model):
    """
    Professional profile information for users with the DOCTOR role.
    Stores clinical credentials, specialties, licensing, and admin verification status.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        help_text='The associated user account.'
    )
    specialization = models.CharField(
        max_length=100,
        help_text='Primary medical specialization (e.g. Cardiology, Neurology, General Medicine).'
    )
    qualification = models.CharField(
        max_length=150,
        help_text='Educational qualifications (e.g. MBBS, MD, MS, FRCS).'
    )
    license_number = models.CharField(
        max_length=50,
        unique=True,
        help_text='Medical council license/registration number.'
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        help_text='Years of clinical medical practice.'
    )
    bio = models.TextField(
        blank=True,
        help_text='Professional clinical summary and background.'
    )
    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Standard consultation fee in local currency.'
    )
    profile_photo = models.ImageField(
        upload_to='doctors/photos/',
        null=True,
        blank=True,
        help_text='Doctor professional headshot.'
    )
    is_approved = models.BooleanField(
        default=False,
        help_text='Verification approval status by MediConnect administrator.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'

    def __str__(self):
        approval_status = "Approved" if self.is_approved else "Pending Verification"
        return f"Dr. {self.user.get_full_name() or self.user.username} ({self.specialization}) - [{approval_status}]"


class DoctorAvailability(models.Model):
    """
    Defines a doctor's working hours for a specific day of the week.
    Slot duration determines how appointments are chunked on that day.
    One record per day (enforced by unique_together).
    """
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField(help_text='Clinic opening time for this day.')
    end_time = models.TimeField(help_text='Clinic closing time for this day.')
    slot_duration_minutes = models.PositiveIntegerField(
        default=30,
        help_text='Appointment slot length in minutes (e.g. 30 = two slots per hour).'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Uncheck to mark this day as unavailable without deleting.'
    )

    class Meta:
        unique_together = ('doctor', 'day_of_week')
        ordering = ['day_of_week', 'start_time']
        verbose_name = 'Doctor Availability'
        verbose_name_plural = 'Doctor Availabilities'

    def __str__(self):
        return (
            f"{self.doctor.user.get_full_name()} - "
            f"{self.get_day_of_week_display()} "
            f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"
        )

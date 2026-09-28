from django.db import models
from django.conf import settings


class PatientProfile(models.Model):
    """
    Detailed profile information for users with the PATIENT role.
    Maintains clinical demographics, contact information, and emergency contacts.
    """
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'

    class BloodGroup(models.TextChoices):
        A_POS = 'A+', 'A+'
        A_NEG = 'A-', 'A-'
        B_POS = 'B+', 'B+'
        B_NEG = 'B-', 'B-'
        AB_POS = 'AB+', 'AB+'
        AB_NEG = 'AB-', 'AB-'
        O_POS = 'O+', 'O+'
        O_NEG = 'O-', 'O-'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        help_text='The associated user account.'
    )
    date_of_birth = models.DateField(
        null=True,
        blank=True,
        help_text='Patient date of birth.'
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.MALE,
        help_text='Patient gender.'
    )
    blood_group = models.CharField(
        max_length=5,
        choices=BloodGroup.choices,
        blank=True,
        null=True,
        help_text='Patient blood group.'
    )
    address = models.TextField(
        blank=True,
        help_text='Residential street address.'
    )
    emergency_contact_name = models.CharField(
        max_length=100,
        blank=True,
        help_text='Name of emergency contact person.'
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text='Phone number of emergency contact.'
    )
    profile_photo = models.ImageField(
        upload_to='patients/photos/',
        null=True,
        blank=True,
        help_text='Patient profile picture.'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"

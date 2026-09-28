import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile, DoctorAvailability
from appointments.models import Appointment
from medical_records.models import MedicalDocument, ConsultationNote
from notifications.models import Notification
from django.core.files.base import ContentFile

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates MediConnect with turnkey demo seed data for evaluation and portfolio demonstration.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE("Initializing MediConnect demonstration database seed..."))

        # 1. Administrator Account
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@mediconnect.org',
                'first_name': 'System',
                'last_name': 'Administrator',
                'role': User.Role.ADMIN,
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('AdminPassword123!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("[OK] Admin created: admin / AdminPassword123!"))

        # 2. Doctor 1: Cardiology (Approved)
        doc1_user, _ = User.objects.get_or_create(
            username='dr_smith',
            defaults={
                'email': 'smith@mediconnect.org',
                'first_name': 'Marcus',
                'last_name': 'Smith',
                'role': User.Role.DOCTOR,
                'phone_number': '+1-555-0101',
            }
        )
        doc1_user.set_password('DoctorPassword123!')
        doc1_user.save()

        doc1_profile, _ = DoctorProfile.objects.get_or_create(
            user=doc1_user,
            defaults={
                'specialization': 'Cardiology',
                'qualification': 'MBBS, MD (Cardiology), FACC',
                'license_number': 'CARD-NY-84920',
                'experience_years': 14,
                'consultation_fee': 95.00,
                'bio': 'Board-certified cardiologist specializing in preventive cardiology, hypertension, and cardiovascular health management.',
                'is_approved': True,
            }
        )
        doc1_profile.is_approved = True
        doc1_profile.save()

        # Doctor 1 Availability (Mon-Fri 09:00 - 17:00, 30 min slots)
        for day in range(5):  # 0=Monday to 4=Friday
            DoctorAvailability.objects.get_or_create(
                doctor=doc1_profile,
                day_of_week=day,
                defaults={
                    'start_time': datetime.time(9, 0),
                    'end_time': datetime.time(17, 0),
                    'slot_duration_minutes': 30,
                    'is_active': True,
                }
            )

        # 3. Doctor 2: Neurology (Approved)
        doc2_user, _ = User.objects.get_or_create(
            username='dr_jones',
            defaults={
                'email': 'jones@mediconnect.org',
                'first_name': 'Elena',
                'last_name': 'Jones',
                'role': User.Role.DOCTOR,
                'phone_number': '+1-555-0102',
            }
        )
        doc2_user.set_password('DoctorPassword123!')
        doc2_user.save()

        doc2_profile, _ = DoctorProfile.objects.get_or_create(
            user=doc2_user,
            defaults={
                'specialization': 'Neurology',
                'qualification': 'MD (Neurology), PhD, FAAN',
                'license_number': 'NEURO-MA-61029',
                'experience_years': 11,
                'consultation_fee': 120.00,
                'bio': 'Consultant neurologist with clinical expertise in headache medicine, peripheral neuropathies, and migraine care.',
                'is_approved': True,
            }
        )
        doc2_profile.is_approved = True
        doc2_profile.save()

        for day in [0, 2, 4]:  # Mon, Wed, Fri
            DoctorAvailability.objects.get_or_create(
                doctor=doc2_profile,
                day_of_week=day,
                defaults={
                    'start_time': datetime.time(10, 0),
                    'end_time': datetime.time(16, 0),
                    'slot_duration_minutes': 30,
                    'is_active': True,
                }
            )

        # 4. Doctor 3: Dermatology (Pending Verification - demonstrates admin review)
        doc3_user, _ = User.objects.get_or_create(
            username='dr_williams',
            defaults={
                'email': 'williams@mediconnect.org',
                'first_name': 'David',
                'last_name': 'Williams',
                'role': User.Role.DOCTOR,
                'phone_number': '+1-555-0103',
            }
        )
        doc3_user.set_password('DoctorPassword123!')
        doc3_user.save()

        DoctorProfile.objects.get_or_create(
            user=doc3_user,
            defaults={
                'specialization': 'Dermatology',
                'qualification': 'MBBS, MD (Dermatology)',
                'license_number': 'DERM-CA-44910',
                'experience_years': 6,
                'consultation_fee': 70.00,
                'bio': 'Clinical dermatologist specializing in eczema, contact dermatitis, and skin cancer surveillance.',
                'is_approved': False,  # Pending
            }
        )

        # 5. Patient 1: Alice Walker
        pat1_user, _ = User.objects.get_or_create(
            username='patient_alice',
            defaults={
                'email': 'alice@mediconnect.org',
                'first_name': 'Alice',
                'last_name': 'Walker',
                'role': User.Role.PATIENT,
                'phone_number': '+1-555-0201',
            }
        )
        pat1_user.set_password('PatientPassword123!')
        pat1_user.save()

        pat1_profile, _ = PatientProfile.objects.get_or_create(
            user=pat1_user,
            defaults={
                'gender': PatientProfile.Gender.FEMALE,
                'blood_group': PatientProfile.BloodGroup.O_POS,
                'date_of_birth': datetime.date(1992, 4, 15),
                'emergency_contact_name': 'Robert Walker',
                'emergency_contact_phone': '+1-555-0209',
                'address': '742 Evergreen Terrace, Springfield',
            }
        )

        # 6. Patient 2: Bob Taylor
        pat2_user, _ = User.objects.get_or_create(
            username='patient_bob',
            defaults={
                'email': 'bob@mediconnect.org',
                'first_name': 'Bob',
                'last_name': 'Taylor',
                'role': User.Role.PATIENT,
                'phone_number': '+1-555-0202',
            }
        )
        pat2_user.set_password('PatientPassword123!')
        pat2_user.save()

        PatientProfile.objects.get_or_create(
            user=pat2_user,
            defaults={
                'gender': PatientProfile.Gender.MALE,
                'blood_group': PatientProfile.BloodGroup.A_POS,
                'date_of_birth': datetime.date(1988, 11, 22),
            }
        )

        # 7. Sample Appointments
        today = timezone.now().date()
        tomorrow = today + datetime.timedelta(days=1)
        next_week = today + datetime.timedelta(days=7)

        # Confirmed upcoming appointment
        appt1, _ = Appointment.objects.get_or_create(
            patient=pat1_user,
            doctor=doc1_profile,
            appointment_date=tomorrow,
            start_time=datetime.time(10, 0),
            defaults={
                'end_time': datetime.time(10, 30),
                'status': Appointment.Status.CONFIRMED,
                'reason': 'Routine blood pressure review and cardiovascular follow-up.',
            }
        )

        # Completed appointment with consultation note
        yesterday = today - datetime.timedelta(days=2)
        appt2, _ = Appointment.objects.get_or_create(
            patient=pat1_user,
            doctor=doc1_profile,
            appointment_date=yesterday,
            start_time=datetime.time(14, 0),
            defaults={
                'end_time': datetime.time(14, 30),
                'status': Appointment.Status.COMPLETED,
                'reason': 'Initial consultation for occasional mild palpitations.',
                'doctor_notes': 'Normal heart sounds. EKG sinus rhythm. Advised hydration and follow-up in 3 months.',
            }
        )

        ConsultationNote.objects.get_or_create(
            appointment=appt2,
            defaults={
                'doctor': doc1_profile,
                'clinical_observations': 'Blood pressure 122/78 mmHg. Resting pulse 68 bpm. Electrocardiogram indicates normal sinus rhythm without ischemic changes.',
                'follow_up_instructions': 'Maintain standard daily hydration (2L/day). Log any palpitations. Follow up in 3 months.',
                'follow_up_date': today + datetime.timedelta(days=90),
            }
        )

        # 8. Sample Medical Documents
        dummy_pdf = ContentFile(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n%%EOF", name="Comprehensive_Metabolic_Panel.pdf")
        MedicalDocument.objects.get_or_create(
            patient=pat1_user,
            title='Comprehensive Metabolic Panel (CMP)',
            defaults={
                'document_type': MedicalDocument.DocumentType.LAB_REPORT,
                'file': dummy_pdf,
                'description': 'Routine fasting metabolic panel and kidney function markers.',
                'appointment': appt2,
            }
        )

        # 9. In-App Notifications
        Notification.objects.get_or_create(
            recipient=pat1_user,
            title='Appointment Confirmed with Dr. Marcus Smith',
            defaults={
                'notification_type': Notification.NotificationType.APPOINTMENT_CONFIRMED,
                'message': f'Your appointment on {tomorrow} at 10:00 AM has been confirmed by Dr. Marcus Smith.',
                'is_read': False,
                'related_appointment_id': appt1.pk,
            }
        )

        Notification.objects.get_or_create(
            recipient=doc1_user,
            title='New Appointment Scheduled',
            defaults={
                'notification_type': Notification.NotificationType.APPOINTMENT_BOOKED,
                'message': f'Patient Alice Walker booked consultation on {tomorrow} at 10:00 AM.',
                'is_read': True,
                'related_appointment_id': appt1.pk,
            }
        )

        self.stdout.write(self.style.SUCCESS("[OK] Seed data generation complete!"))
        self.stdout.write("\n" + "=" * 55)
        self.stdout.write(self.style.SUCCESS("DEMO ACCOUNTS READY TO TEST:"))
        self.stdout.write("  Admin:     admin           / AdminPassword123!")
        self.stdout.write("  Doctor:    dr_smith        / DoctorPassword123! (Cardiology, Approved)")
        self.stdout.write("  Doctor:    dr_williams     / DoctorPassword123! (Dermatology, Pending Review)")
        self.stdout.write("  Patient:   patient_alice   / PatientPassword123!")
        self.stdout.write("  Patient:   patient_bob     / PatientPassword123!")
        self.stdout.write("=" * 55)

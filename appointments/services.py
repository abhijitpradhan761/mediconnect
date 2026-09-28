from django.db import transaction
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta, date
from .models import Appointment
from doctors.models import DoctorProfile, DoctorAvailability


def book_appointment(patient_user, doctor_profile_id: int, appointment_date: date,
                     slot_time_str: str, reason: str = '') -> Appointment:
    """
    Books one appointment slot. Uses select_for_update() inside an atomic transaction
    to prevent race-condition double booking.
    Raises django.core.exceptions.ValidationError on any failure.
    """
    from doctors.services import get_available_slots

    try:
        doctor_profile = DoctorProfile.objects.get(pk=doctor_profile_id, is_approved=True)
    except DoctorProfile.DoesNotExist:
        raise ValidationError("Doctor not found or not yet approved.")

    if appointment_date < date.today():
        raise ValidationError("Cannot book an appointment in the past.")

    slots = get_available_slots(doctor_profile, appointment_date)
    available_times = [s['time'] for s in slots if s['available']]

    if not available_times:
        raise ValidationError("No available slots on this date. Please choose another day.")

    if slot_time_str not in available_times:
        raise ValidationError("This time slot is unavailable. Please choose another.")

    day_of_week = appointment_date.weekday()
    availability = DoctorAvailability.objects.get(
        doctor=doctor_profile, day_of_week=day_of_week, is_active=True
    )

    start_time = datetime.strptime(slot_time_str, '%H:%M').time()
    end_dt = datetime.combine(appointment_date, start_time) + timedelta(minutes=availability.slot_duration_minutes)
    end_time = end_dt.time()

    with transaction.atomic():
        # Lock competing rows to prevent concurrent double booking
        conflict = (
            Appointment.objects
            .select_for_update()
            .filter(
                doctor=doctor_profile,
                appointment_date=appointment_date,
                start_time=start_time,
                status__in=['PENDING', 'CONFIRMED']
            )
            .exists()
        )
        if conflict:
            raise ValidationError("This slot was just booked by another patient. Please choose a different time.")

        appointment = Appointment.objects.create(
            patient=patient_user,
            doctor=doctor_profile,
            appointment_date=appointment_date,
            start_time=start_time,
            end_time=end_time,
            status=Appointment.Status.PENDING,
            reason=reason,
        )

    # Send notifications (best-effort)
    try:
        from notifications.services import notify_appointment_booked
        notify_appointment_booked(appointment)
    except Exception:
        pass

    return appointment


def cancel_appointment(appointment_id: int, requesting_user) -> Appointment:
    """
    Cancels an appointment. Raises ValidationError on permission/state issues.
    Patients can cancel their own; Doctors can cancel theirs; Admins can cancel any.
    """
    try:
        appt = Appointment.objects.select_related('patient', 'doctor__user').get(pk=appointment_id)
    except Appointment.DoesNotExist:
        raise ValidationError("Appointment not found.")

    is_patient_owner = requesting_user.is_patient and appt.patient == requesting_user
    is_doctor_owner = requesting_user.is_doctor and appt.doctor.user == requesting_user

    if not (is_patient_owner or is_doctor_owner or requesting_user.is_administrator):
        raise ValidationError("You do not have permission to cancel this appointment.")

    if appt.status == Appointment.Status.COMPLETED:
        raise ValidationError("Completed appointments cannot be cancelled.")
    if appt.status == Appointment.Status.CANCELLED:
        raise ValidationError("This appointment is already cancelled.")

    appt.status = Appointment.Status.CANCELLED
    appt.save()

    try:
        from notifications.services import notify_appointment_status_changed
        notify_appointment_status_changed(appt)
    except Exception:
        pass

    return appt

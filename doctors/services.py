from datetime import datetime, timedelta, date
from .models import DoctorAvailability


def get_available_slots(doctor_profile, target_date: date):
    """
    Returns a list of slot dicts for a doctor on a given date.
    Each dict: {'time': 'HH:MM', 'available': True/False}
    Excludes slots booked with PENDING or CONFIRMED appointments.
    """
    day_of_week = target_date.weekday()
    try:
        availability = DoctorAvailability.objects.get(
            doctor=doctor_profile,
            day_of_week=day_of_week,
            is_active=True
        )
    except DoctorAvailability.DoesNotExist:
        return []

    # Import here to avoid circular imports
    from appointments.models import Appointment
    booked_starts = set(
        Appointment.objects.filter(
            doctor=doctor_profile,
            appointment_date=target_date,
            status__in=['PENDING', 'CONFIRMED']
        ).values_list('start_time', flat=True)
    )

    slots = []
    current = datetime.combine(target_date, availability.start_time)
    end = datetime.combine(target_date, availability.end_time)
    duration = timedelta(minutes=availability.slot_duration_minutes)

    while current + duration <= end:
        is_booked = current.time() in booked_starts
        slots.append({
            'time': current.strftime('%H:%M'),
            'available': not is_booked,
        })
        current += duration

    return slots

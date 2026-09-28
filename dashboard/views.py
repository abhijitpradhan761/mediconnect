import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator
from accounts.decorators import patient_required, doctor_required, admin_required
from accounts.models import User
from patients.models import PatientProfile
from doctors.models import DoctorProfile, DoctorAvailability
from appointments.models import Appointment
from medical_records.models import MedicalDocument
from notifications.models import Notification
from notifications.services import notify_doctor_approved


@patient_required
def patient_dashboard_view(request):
    """Full-featured patient workspace dashboard."""
    patient_profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    today = timezone.now().date()

    upcoming_appointments = Appointment.objects.filter(
        patient=request.user,
        appointment_date__gte=today,
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('doctor__user').order_by('appointment_date', 'start_time')[:5]

    recent_documents = MedicalDocument.objects.filter(
        patient=request.user
    ).order_by('-uploaded_at')[:4]

    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        is_read=False
    )[:5]

    context = {
        'profile': patient_profile,
        'user': request.user,
        'upcoming_appointments': upcoming_appointments,
        'recent_documents': recent_documents,
        'unread_notifications': unread_notifications,
        'today': today,
    }
    return render(request, 'dashboard/patient_dashboard.html', context)


@doctor_required
def doctor_dashboard_view(request):
    """Full-featured doctor clinical workspace dashboard."""
    doctor_profile, _ = DoctorProfile.objects.get_or_create(user=request.user)
    today = timezone.now().date()

    today_appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        appointment_date=today
    ).select_related('patient').order_by('start_time')

    upcoming_appointments = Appointment.objects.filter(
        doctor=doctor_profile,
        appointment_date__gt=today,
        status__in=['PENDING', 'CONFIRMED']
    ).select_related('patient').order_by('appointment_date', 'start_time')[:5]

    pending_count = Appointment.objects.filter(
        doctor=doctor_profile,
        status='PENDING'
    ).count()

    confirmed_count = Appointment.objects.filter(
        doctor=doctor_profile,
        status='CONFIRMED'
    ).count()

    completed_count = Appointment.objects.filter(
        doctor=doctor_profile,
        status='COMPLETED'
    ).count()

    availabilities = doctor_profile.availabilities.filter(is_active=True).order_by('day_of_week')

    context = {
        'profile': doctor_profile,
        'user': request.user,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'pending_count': pending_count,
        'confirmed_count': confirmed_count,
        'completed_count': completed_count,
        'availabilities': availabilities,
        'today': today,
    }
    return render(request, 'dashboard/doctor_dashboard.html', context)


@admin_required
def admin_dashboard_view(request):
    """Administrator analytics and oversight console."""
    today = timezone.now().date()

    total_patients = User.objects.filter(role=User.Role.PATIENT).count()
    total_doctors = User.objects.filter(role=User.Role.DOCTOR).count()
    pending_doctors_count = DoctorProfile.objects.filter(is_approved=False).count()
    approved_doctors_count = DoctorProfile.objects.filter(is_approved=True).count()

    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='PENDING').count()
    confirmed_appointments = Appointment.objects.filter(status='CONFIRMED').count()
    completed_appointments = Appointment.objects.filter(status='COMPLETED').count()
    cancelled_appointments = Appointment.objects.filter(status='CANCELLED').count()

    # Monthly trends for Chart.js
    monthly_data = (
        Appointment.objects
        .annotate(month=TruncMonth('appointment_date'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )[:6]

    monthly_labels = [item['month'].strftime('%b %Y') for item in monthly_data if item['month']]
    monthly_counts = [item['count'] for item in monthly_data if item['month']]

    # Fallback chart data if new installation
    if not monthly_labels:
        monthly_labels = [today.strftime('%b %Y')]
        monthly_counts = [total_appointments]

    pending_doctor_profiles = DoctorProfile.objects.filter(
        is_approved=False
    ).select_related('user').order_by('-created_at')[:5]

    recent_appointments = Appointment.objects.select_related(
        'patient', 'doctor__user'
    ).order_by('-created_at')[:8]

    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'pending_doctors_count': pending_doctors_count,
        'approved_doctors_count': approved_doctors_count,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'monthly_labels_json': json.dumps(monthly_labels),
        'monthly_counts_json': json.dumps(monthly_counts),
        'pending_doctor_profiles': pending_doctor_profiles,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@admin_required
def admin_patients_view(request):
    """View, search, and manage registered patients."""
    query = request.GET.get('q', '').strip()
    patients = User.objects.filter(role=User.Role.PATIENT).select_related('patient_profile').order_by('-date_joined')

    if query:
        patients = patients.filter(
            username__icontains=query
        ) | patients.filter(
            email__icontains=query
        ) | patients.filter(
            first_name__icontains=query
        ) | patients.filter(
            last_name__icontains=query
        )

    paginator = Paginator(patients, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/admin_patients.html', {
        'page_obj': page_obj,
        'query': query,
    })


@admin_required
def admin_doctors_view(request):
    """View, search, and approve/disable doctor accounts."""
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')

    doctors = DoctorProfile.objects.select_related('user').order_by('-created_at')

    if query:
        doctors = doctors.filter(
            user__username__icontains=query
        ) | doctors.filter(
            user__first_name__icontains=query
        ) | doctors.filter(
            specialization__icontains=query
        ) | doctors.filter(
            license_number__icontains=query
        )

    if status_filter == 'pending':
        doctors = doctors.filter(is_approved=False)
    elif status_filter == 'approved':
        doctors = doctors.filter(is_approved=True)

    paginator = Paginator(doctors, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/admin_doctors.html', {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
    })


@admin_required
def admin_approve_doctor_view(request, pk):
    """Approve a doctor's credentials and dispatch notification."""
    if request.method == 'POST':
        doctor = get_object_or_404(DoctorProfile, pk=pk)
        doctor.is_approved = True
        doctor.save()
        notify_doctor_approved(doctor)
        messages.success(request, f"Dr. {doctor.user.get_full_name()} has been approved successfully.")
    return redirect('admin_doctors')


@admin_required
def admin_revoke_doctor_view(request, pk):
    """Revoke approval for a doctor."""
    if request.method == 'POST':
        doctor = get_object_or_404(DoctorProfile, pk=pk)
        doctor.is_approved = False
        doctor.save()
        messages.warning(request, f"Approval for Dr. {doctor.user.get_full_name()} has been suspended.")
    return redirect('admin_doctors')


@admin_required
def admin_toggle_user_active_view(request, user_id):
    """Activate or deactivate a user account."""
    if request.method == 'POST':
        target_user = get_object_or_404(User, pk=user_id)
        if target_user.is_superuser:
            messages.error(request, "Cannot deactivate superuser accounts.")
            return redirect('admin_patients')
        target_user.is_active = not target_user.is_active
        target_user.save()
        state = "activated" if target_user.is_active else "deactivated"
        messages.info(request, f"Account for {target_user.username} has been {state}.")
    return redirect('admin_patients')


@admin_required
def admin_appointments_view(request):
    """Global appointment monitoring and filtering."""
    status_filter = request.GET.get('status', '')
    query = request.GET.get('q', '').strip()

    appointments = Appointment.objects.select_related('patient', 'doctor__user').order_by('-appointment_date', '-start_time')

    if status_filter:
        appointments = appointments.filter(status=status_filter)

    if query:
        appointments = appointments.filter(
            patient__username__icontains=query
        ) | appointments.filter(
            patient__first_name__icontains=query
        ) | appointments.filter(
            doctor__user__first_name__icontains=query
        ) | appointments.filter(
            doctor__specialization__icontains=query
        )

    paginator = Paginator(appointments, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/admin_appointments.html', {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'query': query,
        'Status': Appointment.Status,
    })


@admin_required
def admin_reports_view(request):
    """Detailed analytics and statistics report view."""
    # Specialization distribution
    specialization_stats = (
        DoctorProfile.objects
        .values('specialization')
        .annotate(doctor_count=Count('id'))
        .order_by('-doctor_count')
    )

    # Status breakdown
    status_stats = (
        Appointment.objects
        .values('status')
        .annotate(count=Count('id'))
        .order_by('status')
    )

    status_labels = [item['status'] for item in status_stats]
    status_counts = [item['count'] for item in status_stats]

    context = {
        'specialization_stats': specialization_stats,
        'status_stats': status_stats,
        'status_labels_json': json.dumps(status_labels),
        'status_counts_json': json.dumps(status_counts),
        'total_appointments': Appointment.objects.count(),
        'total_patients': User.objects.filter(role=User.Role.PATIENT).count(),
        'total_doctors': DoctorProfile.objects.count(),
    }
    return render(request, 'dashboard/admin_reports.html', context)

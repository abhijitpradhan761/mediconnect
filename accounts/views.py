from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home_view(request):
    """Public home landing page for MediConnect."""
    return render(request, 'home.html')


@login_required
def dashboard_redirect_view(request):
    """
    Redirects authenticated users to their respective role-based dashboards:
    - Patients -> /dashboard/patient/
    - Doctors -> /dashboard/doctor/
    - Administrators -> /dashboard/admin/
    """
    user = request.user
    if user.is_administrator:
        return redirect('admin_dashboard')
    elif user.is_doctor:
        return redirect('doctor_dashboard')
    elif user.is_patient:
        return redirect('patient_dashboard')
    return redirect('home')


def register_view(request):
    """
    Registration gateway placeholder for Phase 1.
    Fully implemented with Patient & Doctor registration in Phase 2.
    """
    messages.info(request, "Registration system initialized. Complete registration workflows will be activated in Phase 2.")
    return render(request, 'home.html')

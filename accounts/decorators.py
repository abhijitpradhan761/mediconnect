from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages


def patient_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a patient.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_patient:
            messages.error(request, "Access restricted: This area is reserved for Patients.")
            raise PermissionDenied("User is not a patient.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def doctor_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is a doctor.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_doctor:
            messages.error(request, "Access restricted: This area is reserved for Doctors.")
            raise PermissionDenied("User is not a doctor.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def approved_doctor_required(view_func):
    """
    Decorator checking doctor login and admin verification status.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_doctor:
            messages.error(request, "Access restricted: This area is reserved for Doctors.")
            raise PermissionDenied("User is not a doctor.")
        if not hasattr(request.user, 'doctor_profile') or not request.user.doctor_profile.is_approved:
            messages.warning(request, "Your medical license verification is currently under review by MediConnect administrators.")
            return redirect('doctor_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    """
    Decorator for views that checks that the user is logged in and is an administrator.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_administrator:
            messages.error(request, "Access restricted: Administrator privileges required.")
            raise PermissionDenied("User is not an administrator.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

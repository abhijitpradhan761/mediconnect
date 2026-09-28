from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PatientRegistrationForm, DoctorRegistrationForm, UserLoginForm


def home_view(request):
    """Public home landing page for MediConnect."""
    return render(request, 'home.html')


def register_choice_view(request):
    """Entry page allowing the user to select their registration role."""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')
    return render(request, 'accounts/register_choice.html')


def patient_register_view(request):
    """Registration view for patients."""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to MediConnect, {user.first_name}! Your patient account has been created.")
            return redirect('patient_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PatientRegistrationForm()

    return render(request, 'accounts/register_patient.html', {'form': form})


def doctor_register_view(request):
    """Registration view for doctors."""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = DoctorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Thank you, Dr. {user.last_name or user.username}! Your registration was submitted successfully. "
                "An administrator will verify your credentials before your public profile becomes active."
            )
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = DoctorRegistrationForm()

    return render(request, 'accounts/register_doctor.html', {'form': form})


def login_view(request):
    """Authentication view supporting both Username and Email."""
    if request.user.is_authenticated:
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.get_full_name() or user.username}!")
            # Check for redirect next param
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('dashboard_redirect')
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Logout handler terminating active session."""
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('home')


@login_required
def dashboard_redirect_view(request):
    """
    Role-based dashboard dispatcher.
    Routes authenticated users strictly to their designated workspace.
    """
    user = request.user
    if user.is_administrator:
        return redirect('admin_dashboard')
    elif user.is_doctor:
        return redirect('doctor_dashboard')
    elif user.is_patient:
        return redirect('patient_dashboard')
    return redirect('home')

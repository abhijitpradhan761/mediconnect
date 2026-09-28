from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from accounts.decorators import doctor_required
from .models import DoctorProfile, DoctorAvailability
from .forms import AvailabilityForm


class DoctorListView(View):
    """Public listing of all approved doctors with optional specialization filter."""

    def get(self, request):
        specialization = request.GET.get('specialization', '').strip()
        doctors = DoctorProfile.objects.filter(is_approved=True).select_related('user')
        if specialization:
            doctors = doctors.filter(specialization__icontains=specialization)

        specializations = (
            DoctorProfile.objects
            .filter(is_approved=True)
            .values_list('specialization', flat=True)
            .distinct()
            .order_by('specialization')
        )
        return render(request, 'doctors/doctor_list.html', {
            'doctors': doctors,
            'specializations': specializations,
            'selected_spec': specialization,
        })


class DoctorDetailView(View):
    """Public doctor profile page with availability grid."""

    def get(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, pk=pk, is_approved=True)
        availabilities = doctor.availabilities.filter(is_active=True).order_by('day_of_week')
        return render(request, 'doctors/doctor_detail.html', {
            'doctor': doctor,
            'availabilities': availabilities,
        })


@method_decorator(doctor_required, name='dispatch')
class DoctorAvailabilityListView(View):
    """Doctor's own availability schedule management."""

    def get(self, request):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        availabilities = profile.availabilities.all().order_by('day_of_week')
        return render(request, 'doctors/availability_list.html', {
            'availabilities': availabilities,
            'profile': profile,
        })


@method_decorator(doctor_required, name='dispatch')
class DoctorAvailabilityCreateView(View):
    """Create a new availability slot for a day."""

    def get(self, request):
        form = AvailabilityForm()
        return render(request, 'doctors/availability_form.html', {'form': form, 'action': 'Add'})

    def post(self, request):
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            profile = get_object_or_404(DoctorProfile, user=request.user)
            avail = form.save(commit=False)
            avail.doctor = profile
            try:
                avail.save()
                messages.success(request, f"Availability for {avail.get_day_of_week_display()} added successfully.")
                return redirect('doctor_availability')
            except Exception:
                messages.error(request, "You already have availability set for that day. Please edit the existing one.")
        return render(request, 'doctors/availability_form.html', {'form': form, 'action': 'Add'})


@method_decorator(doctor_required, name='dispatch')
class DoctorAvailabilityUpdateView(View):
    """Edit an existing availability slot."""

    def get(self, request, pk):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        avail = get_object_or_404(DoctorAvailability, pk=pk, doctor=profile)
        form = AvailabilityForm(instance=avail)
        return render(request, 'doctors/availability_form.html', {'form': form, 'action': 'Edit', 'avail': avail})

    def post(self, request, pk):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        avail = get_object_or_404(DoctorAvailability, pk=pk, doctor=profile)
        form = AvailabilityForm(request.POST, instance=avail)
        if form.is_valid():
            form.save()
            messages.success(request, "Availability updated.")
            return redirect('doctor_availability')
        return render(request, 'doctors/availability_form.html', {'form': form, 'action': 'Edit', 'avail': avail})


@method_decorator(doctor_required, name='dispatch')
class DoctorAvailabilityDeleteView(View):
    """Delete an availability slot (POST only)."""

    def post(self, request, pk):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        avail = get_object_or_404(DoctorAvailability, pk=pk, doctor=profile)
        avail.delete()
        messages.success(request, f"Availability for {avail.get_day_of_week_display()} removed.")
        return redirect('doctor_availability')

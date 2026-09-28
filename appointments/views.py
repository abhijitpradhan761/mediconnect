from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.core.exceptions import ValidationError
from accounts.decorators import patient_required, doctor_required
from doctors.models import DoctorProfile
from doctors.services import get_available_slots
from .models import Appointment
from .services import book_appointment, cancel_appointment
from .forms import BookAppointmentForm


@method_decorator(patient_required, name='dispatch')
class PatientAppointmentListView(View):
    def get(self, request):
        today = timezone.now().date()
        tab = request.GET.get('tab', 'upcoming')
        all_appts = Appointment.objects.filter(patient=request.user).select_related('doctor__user')

        if tab == 'history':
            appointments = all_appts.filter(
                appointment_date__lt=today
            ) | all_appts.filter(status__in=['COMPLETED', 'CANCELLED', 'REJECTED'])
            appointments = appointments.distinct()
        else:
            appointments = all_appts.filter(
                appointment_date__gte=today,
                status__in=['PENDING', 'CONFIRMED']
            )

        return render(request, 'appointments/appointment_list.html', {
            'appointments': appointments,
            'tab': tab,
            'today': today,
        })


@method_decorator(patient_required, name='dispatch')
class PatientAppointmentDetailView(View):
    def get(self, request, pk):
        appt = get_object_or_404(Appointment, pk=pk, patient=request.user)
        return render(request, 'appointments/appointment_detail.html', {'appointment': appt})


@method_decorator(patient_required, name='dispatch')
class BookAppointmentView(View):
    def get(self, request, doctor_id):
        doctor = get_object_or_404(DoctorProfile, pk=doctor_id, is_approved=True)
        date_str = request.GET.get('date', '')
        slots = []
        form = BookAppointmentForm()
        if date_str:
            try:
                from datetime import date
                target_date = date.fromisoformat(date_str)
                slots = get_available_slots(doctor, target_date)
                form = BookAppointmentForm(initial={'appointment_date': date_str}, slots=slots)
            except ValueError:
                pass
        return render(request, 'appointments/book_appointment.html', {
            'doctor': doctor, 'form': form, 'slots': slots, 'date_str': date_str
        })

    def post(self, request, doctor_id):
        doctor = get_object_or_404(DoctorProfile, pk=doctor_id, is_approved=True)
        date_str = request.POST.get('appointment_date', '')
        slots = []
        try:
            from datetime import date
            target_date = date.fromisoformat(date_str)
            slots = get_available_slots(doctor, target_date)
        except ValueError:
            pass

        form = BookAppointmentForm(request.POST, slots=slots)
        if form.is_valid():
            try:
                appt = book_appointment(
                    patient_user=request.user,
                    doctor_profile_id=doctor.pk,
                    appointment_date=form.cleaned_data['appointment_date'],
                    slot_time_str=form.cleaned_data['slot_time'],
                    reason=form.cleaned_data.get('reason', '')
                )
                messages.success(request, f"Appointment booked for {appt.appointment_date} at {appt.start_time.strftime('%H:%M')}. Awaiting doctor confirmation.")
                return redirect('appointment_detail', pk=appt.pk)
            except ValidationError as e:
                messages.error(request, str(e.message if hasattr(e, 'message') else e))
        return render(request, 'appointments/book_appointment.html', {
            'doctor': doctor, 'form': form, 'slots': slots, 'date_str': date_str
        })


@method_decorator(patient_required, name='dispatch')
class CancelAppointmentView(View):
    def post(self, request, pk):
        try:
            appt = cancel_appointment(pk, request.user)
            messages.success(request, "Your appointment has been cancelled.")
        except ValidationError as e:
            messages.error(request, str(e.message if hasattr(e, 'message') else e))
        return redirect('patient_appointments')


@method_decorator(doctor_required, name='dispatch')
class DoctorAppointmentListView(View):
    def get(self, request):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        today = timezone.now().date()
        status_filter = request.GET.get('status', '')
        appointments = Appointment.objects.filter(doctor=profile).select_related('patient')
        if status_filter:
            appointments = appointments.filter(status=status_filter)
        return render(request, 'appointments/doctor_appointment_list.html', {
            'appointments': appointments,
            'status_filter': status_filter,
            'today': today,
            'Status': Appointment.Status,
        })


@method_decorator(doctor_required, name='dispatch')
class DoctorAppointmentDetailView(View):
    def get(self, request, pk):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        appt = get_object_or_404(Appointment, pk=pk, doctor=profile)
        return render(request, 'appointments/doctor_appointment_detail.html', {'appointment': appt})


@method_decorator(doctor_required, name='dispatch')
class DoctorUpdateAppointmentStatusView(View):
    def post(self, request, pk):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        appt = get_object_or_404(Appointment, pk=pk, doctor=profile)
        new_status = request.POST.get('status', '')
        doctor_notes = request.POST.get('doctor_notes', '').strip()

        allowed = {
            'CONFIRMED': [Appointment.Status.PENDING],
            'REJECTED': [Appointment.Status.PENDING],
            'COMPLETED': [Appointment.Status.CONFIRMED],
            'CANCELLED': [Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
        }

        if new_status in allowed and appt.status in allowed.get(new_status, []):
            appt.status = new_status
            if doctor_notes:
                appt.doctor_notes = doctor_notes
            appt.save()
            try:
                from notifications.services import notify_appointment_status_changed
                notify_appointment_status_changed(appt)
            except Exception:
                pass
            messages.success(request, f"Appointment marked as {appt.get_status_display()}.")
        else:
            messages.error(request, "Invalid status transition.")

        return redirect('doctor_appointment_detail', pk=pk)

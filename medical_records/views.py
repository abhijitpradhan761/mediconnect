import os
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib import messages
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from accounts.decorators import patient_required, doctor_required
from .models import MedicalDocument, ConsultationNote
from .forms import MedicalDocumentUploadForm, ConsultationNoteForm
from appointments.models import Appointment
from doctors.models import DoctorProfile


@method_decorator(patient_required, name='dispatch')
class PatientDocumentListView(View):
    """List of all health documents uploaded by the patient."""
    def get(self, request):
        documents = MedicalDocument.objects.filter(patient=request.user).select_related('appointment')
        return render(request, 'medical_records/document_list.html', {'documents': documents})


@method_decorator(patient_required, name='dispatch')
class PatientDocumentUploadView(View):
    """Patient uploads a new medical record/document."""
    def get(self, request):
        form = MedicalDocumentUploadForm(patient=request.user)
        return render(request, 'medical_records/document_upload.html', {'form': form})

    def post(self, request):
        form = MedicalDocumentUploadForm(request.POST, request.FILES, patient=request.user)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.patient = request.user
            doc.save()
            messages.success(request, f"Document '{doc.title}' uploaded securely.")
            return redirect('patient_documents')
        return render(request, 'medical_records/document_upload.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class PatientDocumentDetailView(View):
    """View document metadata and action links."""
    def get(self, request, pk):
        doc = get_object_or_404(MedicalDocument, pk=pk)
        # Verify access authorization
        is_owner = (doc.patient == request.user)
        is_attending_doctor = (
            request.user.is_doctor and
            Appointment.objects.filter(
                doctor__user=request.user,
                patient=doc.patient,
                status__in=['CONFIRMED', 'COMPLETED']
            ).exists()
        )
        is_admin = request.user.is_administrator

        if not (is_owner or is_attending_doctor or is_admin):
            return HttpResponseForbidden("You do not have permission to view this document.")

        return render(request, 'medical_records/document_detail.html', {
            'document': doc,
            'is_owner': is_owner,
        })


@method_decorator(patient_required, name='dispatch')
class PatientDocumentDeleteView(View):
    """Patient deletes their own document."""
    def post(self, request, pk):
        doc = get_object_or_404(MedicalDocument, pk=pk, patient=request.user)
        title = doc.title
        if doc.file and os.path.isfile(doc.file.path):
            try:
                os.remove(doc.file.path)
            except OSError:
                pass
        doc.delete()
        messages.success(request, f"Document '{title}' has been deleted.")
        return redirect('patient_documents')


@method_decorator(login_required, name='dispatch')
class SecureDocumentDownloadView(View):
    """
    Secure document download endpoint.
    Guarantees files are NOT exposed publicly without authorization.
    Verifies that the requester is either the owning patient, a doctor with an
    active clinical appointment with this patient, or a platform administrator.
    """
    def get(self, request, pk):
        doc = get_object_or_404(MedicalDocument, pk=pk)
        user = request.user

        is_owner = (doc.patient == user)
        is_attending_doctor = (
            user.is_doctor and
            Appointment.objects.filter(
                doctor__user=user,
                patient=doc.patient,
                status__in=['CONFIRMED', 'COMPLETED']
            ).exists()
        )
        is_admin = user.is_administrator

        if not (is_owner or is_attending_doctor or is_admin):
            return HttpResponseForbidden("Access denied: You are not authorized to access this patient's records.")

        if not doc.file or not os.path.isfile(doc.file.path):
            raise Http404("Document file not found on server storage.")

        filename = os.path.basename(doc.file.name)
        return FileResponse(open(doc.file.path, 'rb'), as_attachment=True, filename=filename)


@method_decorator(doctor_required, name='dispatch')
class DoctorPatientDocumentsView(View):
    """
    Allows a doctor to view documents for patients who have appointments with them.
    Protects private records: only returns documents of legitimate clinical patients.
    """
    def get(self, request):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        # Get all distinct patient IDs who have appointments with this doctor
        patient_ids = Appointment.objects.filter(
            doctor=profile,
            status__in=['CONFIRMED', 'COMPLETED']
        ).values_list('patient_id', flat=True).distinct()

        documents = MedicalDocument.objects.filter(
            patient_id__in=patient_ids
        ).select_related('patient', 'appointment').order_by('-uploaded_at')

        return render(request, 'medical_records/doctor_patient_docs.html', {
            'documents': documents,
            'profile': profile,
        })


@method_decorator(doctor_required, name='dispatch')
class ConsultationNoteCreateView(View):
    """Doctor writes consultation notes after an appointment."""
    def get(self, request, appointment_id):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=profile)
        form = ConsultationNoteForm()
        return render(request, 'medical_records/consultation_note_form.html', {
            'form': form,
            'appointment': appointment,
            'action': 'Record',
        })

    def post(self, request, appointment_id):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        appointment = get_object_or_404(Appointment, pk=appointment_id, doctor=profile)
        form = ConsultationNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.appointment = appointment
            note.doctor = profile
            note.save()
            messages.success(request, "Consultation note saved successfully.")
            return redirect('doctor_appointment_detail', pk=appointment.pk)
        return render(request, 'medical_records/consultation_note_form.html', {
            'form': form,
            'appointment': appointment,
            'action': 'Record',
        })


@method_decorator(doctor_required, name='dispatch')
class ConsultationNoteUpdateView(View):
    """Doctor updates existing consultation notes."""
    def get(self, request, pk):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        note = get_object_or_404(ConsultationNote, pk=pk, doctor=profile)
        form = ConsultationNoteForm(instance=note)
        return render(request, 'medical_records/consultation_note_form.html', {
            'form': form,
            'appointment': note.appointment,
            'action': 'Update',
            'note': note,
        })

    def post(self, request, pk):
        profile = get_object_or_404(DoctorProfile, user=request.user)
        note = get_object_or_404(ConsultationNote, pk=pk, doctor=profile)
        form = ConsultationNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, "Consultation note updated successfully.")
            return redirect('doctor_appointment_detail', pk=note.appointment.pk)
        return render(request, 'medical_records/consultation_note_form.html', {
            'form': form,
            'appointment': note.appointment,
            'action': 'Update',
            'note': note,
        })


@method_decorator(login_required, name='dispatch')
class ConsultationNoteDetailView(View):
    """View consultation note details (patient or attending doctor)."""
    def get(self, request, pk):
        note = get_object_or_404(ConsultationNote, pk=pk)
        user = request.user
        is_patient_owner = (note.appointment.patient == user)
        is_author_doctor = (note.doctor.user == user)
        is_admin = user.is_administrator

        if not (is_patient_owner or is_author_doctor or is_admin):
            return HttpResponseForbidden("Access restricted: You cannot view this consultation note.")

        return render(request, 'medical_records/consultation_note_detail.html', {'note': note})

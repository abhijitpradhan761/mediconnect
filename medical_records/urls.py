from django.urls import path
from . import views

urlpatterns = [
    # Patient Document Management
    path('documents/', views.PatientDocumentListView.as_view(), name='patient_documents'),
    path('documents/upload/', views.PatientDocumentUploadView.as_view(), name='document_upload'),
    path('documents/<int:pk>/', views.PatientDocumentDetailView.as_view(), name='document_detail'),
    path('documents/<int:pk>/delete/', views.PatientDocumentDeleteView.as_view(), name='document_delete'),
    path('documents/<int:pk>/download/', views.SecureDocumentDownloadView.as_view(), name='document_download'),

    # Doctor access to legitimate patient records
    path('doctor/patient-documents/', views.DoctorPatientDocumentsView.as_view(), name='doctor_patient_docs'),

    # Consultation Notes
    path('notes/create/<int:appointment_id>/', views.ConsultationNoteCreateView.as_view(), name='create_consultation_note'),
    path('notes/<int:pk>/edit/', views.ConsultationNoteUpdateView.as_view(), name='edit_consultation_note'),
    path('notes/<int:pk>/', views.ConsultationNoteDetailView.as_view(), name='consultation_note_detail'),
]

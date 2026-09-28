"""
Master URL configuration for MediConnect platform.
Cleanly separates Web Portal routes from REST API endpoints.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Web views
from accounts.views import (
    home_view, login_view, register_choice_view,
    patient_register_view, doctor_register_view, logout_view
)

# API view imports
from accounts import api_views as accounts_api
from doctors import api_views as doctors_api
from appointments import api_views as appointments_api
from medical_records import api_views as records_api
from notifications import api_views as notif_api
from ai_assistant import api_views as ai_api
from dashboard import api_views as dashboard_api

# Unified REST API router
api_patterns = [
    # Authentication & Accounts
    path('auth/register/', accounts_api.RegisterPatientAPIView.as_view(), name='api_register_patient'),
    path('auth/register-doctor/', accounts_api.RegisterDoctorAPIView.as_view(), name='api_register_doctor'),
    path('auth/login/', accounts_api.LoginAPIView.as_view(), name='api_login'),
    path('auth/logout/', accounts_api.LogoutAPIView.as_view(), name='api_logout'),
    path('auth/user/', accounts_api.CurrentUserAPIView.as_view(), name='api_current_user'),

    # Doctors & Availability
    path('doctors/', doctors_api.DoctorListAPIView.as_view(), name='api_doctor_list'),
    path('doctors/<int:pk>/', doctors_api.DoctorDetailAPIView.as_view(), name='api_doctor_detail'),
    path('doctors/<int:pk>/availability/', doctors_api.DoctorAvailabilityAPIView.as_view(), name='api_doctor_availability'),
    path('doctors/<int:pk>/slots/', doctors_api.DoctorSlotsAPIView.as_view(), name='api_doctor_slots'),

    # Appointments Engine
    path('appointments/', appointments_api.AppointmentListCreateAPIView.as_view(), name='api_appointments'),
    path('appointments/<int:pk>/', appointments_api.AppointmentDetailAPIView.as_view(), name='api_appointment_detail'),
    path('appointments/<int:pk>/cancel/', appointments_api.AppointmentCancelAPIView.as_view(), name='api_cancel_appointment'),

    # Medical Records & Notes
    path('medical-records/', records_api.MedicalDocumentAPIView.as_view(), name='api_medical_records'),
    path('medical-records/<int:pk>/', records_api.MedicalDocumentDetailAPIView.as_view(), name='api_medical_record_detail'),
    path('notes/', records_api.ConsultationNoteAPIView.as_view(), name='api_consultation_notes'),

    # In-App Notifications
    path('notifications/', notif_api.NotificationListAPIView.as_view(), name='api_notifications'),
    path('notifications/<int:pk>/', notif_api.NotificationDetailAPIView.as_view(), name='api_notification_detail'),
    path('notifications/unread-count/', notif_api.UnreadNotificationCountAPIView.as_view(), name='api_unread_count'),

    # Responsible AI Assistant
    path('ai/symptom-summary/', ai_api.SymptomSummaryAPIView.as_view(), name='api_ai_symptom_summary'),
    path('ai/questions/', ai_api.DoctorQuestionsAPIView.as_view(), name='api_ai_questions'),
    path('ai/summarize-document/', ai_api.DocumentSummaryAPIView.as_view(), name='api_ai_summarize_document'),

    # Administrative Analytics
    path('admin/dashboard/', dashboard_api.AdminDashboardStatsAPIView.as_view(), name='api_admin_dashboard'),
    path('admin/reports/', dashboard_api.AdminReportsAPIView.as_view(), name='api_admin_reports'),
]

urlpatterns = [
    # System Administration
    path('admin/', admin.site.urls),

    # Public Landing Page
    path('', home_view, name='home'),

    # Direct convenient Auth shortcuts
    path('login/', login_view, name='login'),
    path('register/', register_choice_view, name='register'),
    path('register/patient/', patient_register_view, name='patient_register_direct'),
    path('register/doctor/', doctor_register_view, name='doctor_register_direct'),
    path('logout/', logout_view, name='logout'),

    # Web Applications
    path('accounts/', include('accounts.urls')),
    path('doctors/', include('doctors.urls')),
    path('appointments/', include('appointments.urls')),
    path('medical-records/', include('medical_records.urls')),
    path('notifications/', include('notifications.urls')),
    path('ai/', include('ai_assistant.urls')),
    path('dashboard/', include('dashboard.urls')),

    # REST API Root Router
    path('api/', include(api_patterns)),
]

# Development static & media serving
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

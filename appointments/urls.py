from django.urls import path
from . import views

urlpatterns = [
    # Patient appointment views
    path('', views.PatientAppointmentListView.as_view(), name='patient_appointments'),
    path('book/<int:doctor_id>/', views.BookAppointmentView.as_view(), name='book_appointment'),
    path('<int:pk>/', views.PatientAppointmentDetailView.as_view(), name='appointment_detail'),
    path('<int:pk>/cancel/', views.CancelAppointmentView.as_view(), name='cancel_appointment'),

    # Doctor appointment views
    path('doctor/', views.DoctorAppointmentListView.as_view(), name='doctor_appointments'),
    path('doctor/<int:pk>/', views.DoctorAppointmentDetailView.as_view(), name='doctor_appointment_detail'),
    path('doctor/<int:pk>/status/', views.DoctorUpdateAppointmentStatusView.as_view(), name='update_appointment_status'),
]

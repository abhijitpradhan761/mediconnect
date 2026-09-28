from django.urls import path
from . import views

urlpatterns = [
    # Role Dashboards
    path('patient/', views.patient_dashboard_view, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard_view, name='doctor_dashboard'),
    path('admin/', views.admin_dashboard_view, name='admin_dashboard'),

    # Admin Management Workflows
    path('admin/patients/', views.admin_patients_view, name='admin_patients'),
    path('admin/patients/<int:user_id>/toggle-active/', views.admin_toggle_user_active_view, name='admin_toggle_user_active'),
    path('admin/doctors/', views.admin_doctors_view, name='admin_doctors'),
    path('admin/doctors/<int:pk>/approve/', views.admin_approve_doctor_view, name='admin_approve_doctor'),
    path('admin/doctors/<int:pk>/revoke/', views.admin_revoke_doctor_view, name='admin_revoke_doctor'),
    path('admin/appointments/', views.admin_appointments_view, name='admin_appointments'),
    path('admin/reports/', views.admin_reports_view, name='admin_reports'),
]

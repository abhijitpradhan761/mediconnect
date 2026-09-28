from django.urls import path
from . import views

urlpatterns = [
    # Frontend Authentication & Registration
    path('register/', views.register_choice_view, name='register'),
    path('register/patient/', views.patient_register_view, name='patient_register'),
    path('register/doctor/', views.doctor_register_view, name='doctor_register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/redirect/', views.dashboard_redirect_view, name='dashboard_redirect'),
]

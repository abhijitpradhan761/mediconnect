from django.urls import path
from . import views

urlpatterns = [
    # Public HTML pages
    path('', views.DoctorListView.as_view(), name='doctor_list'),
    path('<int:pk>/', views.DoctorDetailView.as_view(), name='doctor_detail'),

    # Doctor self-management
    path('my/availability/', views.DoctorAvailabilityListView.as_view(), name='doctor_availability'),
    path('my/availability/add/', views.DoctorAvailabilityCreateView.as_view(), name='doctor_availability_create'),
    path('my/availability/<int:pk>/edit/', views.DoctorAvailabilityUpdateView.as_view(), name='doctor_availability_edit'),
    path('my/availability/<int:pk>/delete/', views.DoctorAvailabilityDeleteView.as_view(), name='doctor_availability_delete'),
]

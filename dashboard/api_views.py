from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncMonth
from accounts.permissions import IsAdministrator
from accounts.models import User
from doctors.models import DoctorProfile
from appointments.models import Appointment


class AdminDashboardStatsAPIView(APIView):
    """
    GET /api/admin/dashboard/
    Statistical KPIs for administrative overview.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdministrator]

    def get(self, request):
        data = {
            'total_patients': User.objects.filter(role=User.Role.PATIENT).count(),
            'total_doctors': User.objects.filter(role=User.Role.DOCTOR).count(),
            'approved_doctors': DoctorProfile.objects.filter(is_approved=True).count(),
            'pending_doctors': DoctorProfile.objects.filter(is_approved=False).count(),
            'total_appointments': Appointment.objects.count(),
            'pending_appointments': Appointment.objects.filter(status='PENDING').count(),
            'confirmed_appointments': Appointment.objects.filter(status='CONFIRMED').count(),
            'completed_appointments': Appointment.objects.filter(status='COMPLETED').count(),
            'cancelled_appointments': Appointment.objects.filter(status='CANCELLED').count(),
        }
        return Response(data)


class AdminReportsAPIView(APIView):
    """
    GET /api/admin/reports/
    Monthly breakdown and category distributions.
    """
    permission_classes = [permissions.IsAuthenticated, IsAdministrator]

    def get(self, request):
        monthly = (
            Appointment.objects
            .annotate(month=TruncMonth('appointment_date'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        by_status = (
            Appointment.objects
            .values('status')
            .annotate(count=Count('id'))
        )
        by_specialization = (
            DoctorProfile.objects
            .values('specialization')
            .annotate(count=Count('id'))
            .order_by('-count')
        )

        return Response({
            'monthly_appointments': list(monthly),
            'appointments_by_status': list(by_status),
            'doctors_by_specialization': list(by_specialization),
        })

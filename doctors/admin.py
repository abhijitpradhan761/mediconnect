from django.contrib import admin
from .models import DoctorProfile, DoctorAvailability


@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'license_number', 'experience_years', 'consultation_fee', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'specialization')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization', 'license_number')
    actions = ['approve_doctors', 'revoke_approval']

    @admin.action(description='Approve selected doctors')
    def approve_doctors(self, request, queryset):
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} doctor(s) approved.")

    @admin.action(description='Revoke approval for selected doctors')
    def revoke_approval(self, request, queryset):
        count = queryset.update(is_approved=False)
        self.message_user(request, f"{count} doctor(s) approval revoked.")


@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'get_day_name', 'start_time', 'end_time', 'slot_duration_minutes', 'is_active')
    list_filter = ('day_of_week', 'is_active')

    def get_day_name(self, obj):
        return obj.get_day_of_week_display()
    get_day_name.short_description = 'Day'

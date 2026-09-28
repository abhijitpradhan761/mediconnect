from rest_framework import permissions


class IsPatient(permissions.BasePermission):
    """
    Allows access only to authenticated users with the PATIENT role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_patient
        )


class IsDoctor(permissions.BasePermission):
    """
    Allows access only to authenticated users with the DOCTOR role.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_doctor
        )


class IsApprovedDoctor(permissions.BasePermission):
    """
    Allows access only to authenticated doctors whose medical credentials have been verified.
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated and request.user.is_doctor):
            return False
        return getattr(request.user, 'doctor_profile', None) and request.user.doctor_profile.is_approved


class IsAdministrator(permissions.BasePermission):
    """
    Allows access only to authenticated platform administrators.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.is_administrator
        )

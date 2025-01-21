from rest_framework.permissions import BasePermission

class TwoFactorAuthenticationRequired(BasePermission):
    """
    Ensures that 2FA is required and completed before granting access.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return False

        # Ensure the authentication object exists and has the expected attribute
        auth_data = getattr(request, 'auth', None)
        if auth_data and isinstance(auth_data, dict):
            return auth_data.get('2fa_complete', False)

        # Default to deny access if 2FA completion is not explicitly confirmed
        return False


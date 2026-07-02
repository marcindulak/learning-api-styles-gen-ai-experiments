"""Object-level permissions of the Weather Forecast Service."""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """Reads are public; writes require an authenticated admin user.

    An unauthenticated write is rejected with 401 (DRF raises
    NotAuthenticated because a JWT authenticator is configured), while an
    authenticated non-admin write is rejected with 403.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

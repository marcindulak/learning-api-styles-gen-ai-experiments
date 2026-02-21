from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit/create/delete objects.
    Regular authenticated users have read-only access.
    """

    def has_permission(self, request, view):
        # Allow read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions only for admin users
        return request.user and request.user.is_staff

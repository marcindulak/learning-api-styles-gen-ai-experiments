from rest_framework.permissions import SAFE_METHODS, BasePermission


def is_self_or_admin(user, profile_owner) -> bool:
    """Whether `user` may access the profile belonging to `profile_owner`.

    Shared by the REST permission class below and the GraphQL `user` query
    resolver (weather/schema.py) so the one access rule is defined once.
    """
    return bool(user.is_staff or user == profile_owner)


class IsAdminOrReadOnly(BasePermission):
    """Anyone may read; only an admin (is_staff) user may write."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsSelfOrAdmin(BasePermission):
    """A user may access only their own profile; an admin may access any profile."""

    def has_object_permission(self, request, view, obj):
        return is_self_or_admin(request.user, obj)

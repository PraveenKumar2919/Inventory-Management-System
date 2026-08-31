from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """
    Allows access only to users in the Admin group.
    """

    message = "Admin access required."

    def has_permission(self, request, view):

        user = request.user

        return (
            user
            and user.is_authenticated
            and user.groups.filter(
                name="Admin"
            ).exists()
        )


class IsStaffRole(BasePermission):
    """
    Allows access to Admin and Staff users.
    """

    message = "Staff or Admin access required."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        return user.groups.filter(
            name__in=[
                "Admin",
                "Staff",
            ]
        ).exists()


class IsAdminOrStaffReadOnly(BasePermission):
    """
    Admin and Staff can read.
    Only Admin can modify.
    """

    message = "Admin access required for modification."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in [
            "GET",
            "HEAD",
            "OPTIONS",
        ]:
            return user.groups.filter(
                name__in=[
                    "Admin",
                    "Staff",
                ]
            ).exists()

        return user.groups.filter(
            name="Admin"
        ).exists()
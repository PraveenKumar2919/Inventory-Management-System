from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """
    Only admin/staff users can access.
    """

    message = "Admin access required."

    def has_permission(self, request, view):

        user = request.user

        return bool(
            user
            and user.is_authenticated
            and user.is_staff
        )


class IsStaffOrAdmin(BasePermission):
    """
    Staff or admin users can access.
    """

    message = "Staff or Admin access required."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        return bool(
            user.is_staff
            or user.groups.filter(
                name__in=[
                    "Admin",
                    "Staff",
                    "Inventory Staff",
                ]
            ).exists()
        )


class IsViewer(BasePermission):
    """
    Any authenticated user can view data.
    """

    message = "Authentication required."

    def has_permission(self, request, view):

        return bool(
            request.user
            and request.user.is_authenticated
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Admin users have full access.
    Authenticated users can read data.
    """

    message = "Admin access required for this action."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        # Everyone authenticated can read
        if request.method in SAFE_METHODS:
            return True

        # Only admin/staff can modify
        return bool(
            user.is_staff
            or user.groups.filter(
                name="Admin"
            ).exists()
        )


class IsStaffOrAdminOrReadOnly(BasePermission):
    """
    Authenticated users can read.
    Staff and Admin can access inventory APIs.
    Only Admin can modify inventory master data.
    """

    message = "Admin access required for modification."

    def has_permission(self, request, view):

        user = request.user

        if not user or not user.is_authenticated:
            return False

        # ---------------------------------------------
        # READ
        # ---------------------------------------------

        if request.method in SAFE_METHODS:

            return True

        # ---------------------------------------------
        # WRITE
        # ---------------------------------------------

        return bool(
            user.is_staff
            or user.groups.filter(
                name="Admin"
            ).exists()
        )
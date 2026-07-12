from rest_framework import permissions
from users.models import UserRole

class IsAdmin(permissions.BasePermission):
    """
    Allows access only to ADMIN users.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == UserRole.ADMIN
        )

class IsAssetManagerOrAdmin(permissions.BasePermission):
    """
    Allows access to ADMIN and ASSET_MANAGER users.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.ADMIN, UserRole.ASSET_MANAGER]
        )

class IsDeptHeadOrAbove(permissions.BasePermission):
    """
    Allows access to ADMIN, ASSET_MANAGER, and DEPT_HEAD users.
    """
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [UserRole.ADMIN, UserRole.ASSET_MANAGER, UserRole.DEPT_HEAD]
        )

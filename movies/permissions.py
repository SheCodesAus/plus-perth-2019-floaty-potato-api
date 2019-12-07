from rest_framework import permissions


class IsAdminOrSelf(permissions.BasePermission):
    """
    For Users - Only admin or authenticated user is able to do this
    action (i.e view and edit profile)
    """

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or request.user == obj

class IsAdminUser(permissions.BasePermission):
    """
    For Admin Only - Only admin is able to do this
    action (i.e get list of all users or delete users)
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and requst.user.is_staff

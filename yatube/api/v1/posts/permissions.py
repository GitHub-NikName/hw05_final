from rest_framework import permissions


class UserPermissions(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    message = 'неавтовтовторивизирован или свой пост редактируй'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if view.action in ('create', 'update', 'put'):
            return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in permissions.SAFE_METHODS or
            obj.author == request.user
        )

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Проверка: произведен ли запрос владельцем."""

    def has_object_permission(self, request, view, obj):
        return (obj.user == request.user)

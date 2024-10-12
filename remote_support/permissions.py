from rest_framework import permissions
from .redis_util import getUserBySessionId

class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySessionId(request)
        return bool(user) or request.method in permissions.SAFE_METHODS

class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySessionId(request)
        return bool(user)

class IsHelper(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySessionId(request)
        return bool(user and (user.is_staff or user.is_superuser))
    
class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getUserBySessionId(request)
        return bool(user and user.is_superuser)
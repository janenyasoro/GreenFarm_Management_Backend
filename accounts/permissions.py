from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission that only allows admin users to access the view.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission that only allows owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj == request.user


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission that only allows owners or admins to access the view.
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Admins can access everything
        if request.user.is_admin():
            return True
        
        # Users can only access their own data
        return obj == request.user


class IsAdminOrOwner(permissions.BasePermission):
    """
    Permission that only allows admins or owners to access the view.
    Similar to IsOwnerOrAdmin but for permission level (not object level).
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_admin() or request.user.is_owner())
        )
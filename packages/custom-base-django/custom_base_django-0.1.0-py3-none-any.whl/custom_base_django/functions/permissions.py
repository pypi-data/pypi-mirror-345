from rest_framework import permissions


class HasFunctionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        function_name = view.kwargs.get('function_name')
        if not function_name:
            return True

        metadata = view.registry.get_metadata(function_name)
        if not metadata:
            return False

        required_permission = metadata.get('permission', 'any')

        if required_permission == 'any':
            return True
        elif required_permission == 'authenticated':
            return request.user.is_authenticated
        elif required_permission == 'admin':
            return request.user.is_superuser
        elif required_permission == 'staff':
            return request.user.is_staff

        return False
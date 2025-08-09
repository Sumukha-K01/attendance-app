from rest_framework import permissions
import os
import hmac

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users to access the view.
    """
    def has_permission(self, request, view):
        return request.user.role == 'admin'


class isCron(permissions.BasePermission):
    """Allow access only if request contains a valid X-Cron-Key header.
    header X-Cron-Key: <CRON_SECRET>.
    """
    def has_permission(self, request, view):
        cron_key = request.headers.get('X-Cron-Key')
        expected = os.environ.get('CRON_SECRET')
        return bool(expected and cron_key and hmac.compare_digest(cron_key, expected))
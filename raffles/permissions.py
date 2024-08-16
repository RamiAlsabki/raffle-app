import os
from rest_framework.permissions import BasePermission

SAFE_METHODS = ['GET']

class IsManagerIP(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
         
        client_ip = request.META.get('REMOTE_ADDR')
        managers_ips = os.environ.get('MANAGER_IPS', '').split(',')
        return client_ip in managers_ips
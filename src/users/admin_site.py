from django.conf import settings
from django.contrib.admin import AdminSite
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .auth import user_has_admin_group


class AdminSite(AdminSite):
    def has_permission(self, request):
        return user_has_admin_group(request.user) and super().has_permission(request)

    def login(self, request, extra_context=None):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)
        if not user_has_admin_group(request.user):
            raise PermissionDenied("A auth0 provider admin group is required.")
        return super().login(request, extra_context)

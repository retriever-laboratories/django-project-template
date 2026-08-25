from django.conf import settings
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import urlencode

from oidc_auth.auth import user_has_admin_group


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._requires_login(request):
            login_url = reverse("oidc_login")
            query = urlencode({"next": request.get_full_path()})
            return redirect(f"{login_url}?{query}")

        if self._blocks_admin(request):
            return HttpResponseForbidden("You do not have access to Django admin.")

        return self.get_response(request)

    def _requires_login(self, request):
        if request.user.is_authenticated:
            return False

        path = request.path_info
        return not any(path.startswith(prefix) for prefix in settings.LOGIN_EXEMPT_URLS)

    def _blocks_admin(self, request):
        path = request.path_info
        if not path.startswith("/admin/"):
            return False
        return not user_has_admin_group(request.user)

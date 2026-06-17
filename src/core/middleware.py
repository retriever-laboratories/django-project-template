from django.conf import settings
from django.contrib.auth.views import redirect_to_login


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated or self._is_exempt(request.path_info):
            return self.get_response(request)

        return redirect_to_login(request.get_full_path(), settings.LOGIN_URL)

    def _is_exempt(self, path):
        return any(path.startswith(prefix) for prefix in settings.LOGIN_REQUIRED_EXEMPT_URLS)

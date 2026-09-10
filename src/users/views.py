from authlib.integrations.base_client.errors import OAuthError
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_not_required
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST

from .auth import OIDCClient


def safe_next(request, target):
    if target and url_has_allowed_host_and_scheme(
        target, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return target
    return settings.LOGIN_REDIRECT_URL


@login_not_required
@require_GET
def oidc_login(request):
    request.session["oidc_next"] = safe_next(request, request.GET.get("next"))
    callback = request.build_absolute_uri(reverse("users:callback"))
    return OIDCClient().authorize_redirect(request, callback)


@login_not_required
@require_GET
def oidc_callback(request):
    destination = safe_next(request, request.session.pop("oidc_next", None))
    try:
        user = OIDCClient().authenticate(request)
    except OAuthError:
        return HttpResponseBadRequest("OIDC authentication failed.")
    login(request, user)
    return redirect(destination)


@login_not_required
@require_POST
def oidc_logout(request):
    logout(request)
    return_to = request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL)
    return redirect(OIDCClient().logout_url(return_to))

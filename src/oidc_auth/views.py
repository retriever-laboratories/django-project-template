from django.conf import settings
from django.contrib import auth
from django.contrib import messages
from django.core.exceptions import ImproperlyConfigured
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from oidc_auth.auth import callback_url
from oidc_auth.auth import get_oidc_client
from oidc_auth.auth import provider_logout_url
from oidc_auth.auth import sync_user_from_claims


def _safe_next_url(request):
    next_url = request.GET.get("next") or request.POST.get("next") or "/"
    if url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return "/"


def login(request):
    try:
        client = get_oidc_client()
    except ImproperlyConfigured as exc:
        return HttpResponse(str(exc), status=503)

    request.session["oidc_login_next"] = _safe_next_url(request)
    authorization_params = {}
    if settings.OIDC_AUDIENCE:
        authorization_params["audience"] = settings.OIDC_AUDIENCE

    return client.authorize_redirect(
        request,
        callback_url(request),
        **authorization_params,
    )


def callback(request):
    try:
        token = get_oidc_client().authorize_access_token(request)
    except Exception:
        messages.error(request, "Login failed. Please try again.")
        return redirect(reverse("oidc_login"))

    claims = token.get("userinfo") or {}
    if not claims and "id_token" in token:
        claims = get_oidc_client().parse_id_token(request, token)

    user = sync_user_from_claims(claims)
    auth.login(request, user)
    request.session["oidc_id_token"] = token.get("id_token", "")

    next_url = request.session.pop("oidc_login_next", "/")
    return redirect(next_url)


def logout(request):
    id_token = request.session.get("oidc_id_token")
    try:
        redirect_url = provider_logout_url(request, id_token=id_token)
    except ImproperlyConfigured:
        redirect_url = "/"

    auth.logout(request)
    return redirect(redirect_url)

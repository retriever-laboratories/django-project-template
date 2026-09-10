"""OIDC client for the single configured provider (Auth0 in this deployment)."""

from urllib.parse import urlencode
from uuid import uuid4

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import PermissionDenied
from django.db import transaction


class OIDCClient:
    def __init__(self):
        if not all(
            (
                settings.OIDC_PROVIDER_DOMAIN,
                settings.OIDC_CLIENT_ID,
                settings.OIDC_CLIENT_SECRET,
            )
        ):
            raise ImproperlyConfigured(
                "Configure OIDC_PROVIDER_DOMAIN and OIDC client credentials."
            )
        domain = settings.OIDC_PROVIDER_DOMAIN.strip().rstrip("/")
        if not domain or any(char in domain for char in "/:?#@"):
            raise ImproperlyConfigured(
                "OIDC_PROVIDER_DOMAIN must be a hostname without a scheme or path."
            )
        self.issuer = f"https://{domain}/"
        self.client = OAuth().register(
            "oidc",
            client_id=settings.OIDC_CLIENT_ID,
            client_secret=settings.OIDC_CLIENT_SECRET,
            server_metadata_url=(
                f"{self.issuer.rstrip('/')}/.well-known/openid-configuration"
            ),
            client_kwargs={
                "scope": "openid profile email groups",
                "code_challenge_method": "S256",
                "timeout": 10,
            },
        )

    def authorize_redirect(self, request, redirect_uri):
        kwargs = {"audience": settings.OIDC_AUDIENCE} if settings.OIDC_AUDIENCE else {}
        return self.client.authorize_redirect(request, redirect_uri, **kwargs)

    def authenticate(self, request):
        token = self.client.authorize_access_token(
            request,
            claims_options={"iss": {"essential": True, "value": self.issuer}},
        )
        claims = token.get("userinfo")
        if not claims or claims.get("iss") != self.issuer:
            raise PermissionDenied("Invalid OIDC identity.")
        return self._sync_user_from_claims(claims)

    def logout_url(self, return_to):
        """End the Auth0 browser session and return to an allow-listed URL."""
        query = urlencode({"client_id": settings.OIDC_CLIENT_ID, "returnTo": return_to})
        return f"{self.issuer.rstrip('/')}/v2/logout?{query}"

    @transaction.atomic
    def _sync_user_from_claims(self, claims):  # noqa: ARG002
        """Persist validated ID-token claims; never pass unverified JWT data."""
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject or len(subject) > 255:
            raise PermissionDenied("Invalid OIDC subject.")

        user_model = get_user_model()
        user, _ = user_model.objects.get_or_create(
            subject=subject,
            defaults={"username": f"oidc_{uuid4().hex}", "password": "!"},
        )
        user.is_active = True
        for field, claim in (
            ("email", "email"),
            ("first_name", "given_name"),
            ("last_name", "family_name"),
        ):
            value = claims.get(claim, "")
            if not isinstance(value, str):
                raise PermissionDenied("Invalid OIDC profile.")
            setattr(user, field, value[: user_model._meta.get_field(field).max_length])
        user.set_unusable_password()
        user.save(
            update_fields=[
                "email",
                "first_name",
                "last_name",
                "password",
                "is_active",
            ]
        )
        group_names = claims.get(settings.OIDC_GROUPS_CLAIM, [])
        groups = [Group.objects.get_or_create(name=name)[0] for name in group_names]
        user.groups.set(groups)
        return user


def user_has_admin_group(user):
    """Group eligibility only; does not grant staff or superuser permissions."""
    return bool(
        user.is_authenticated
        and user.is_active
        and user.groups.filter(name__in=settings.OIDC_ADMIN_GROUPS).exists()
    )

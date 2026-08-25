from functools import lru_cache
from urllib.parse import quote_plus
from urllib.parse import urlencode

from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.utils.text import slugify

from oidc_auth.models import UserIdentity

oauth = OAuth()


def _issuer_url():
    issuer = settings.OIDC_ISSUER.strip()
    if not issuer:
        msg = "Set OIDC_PROVIDER_DOMAIN or OIDC_ISSUER before using OIDC login."
        raise ImproperlyConfigured(msg)
    return issuer.rstrip("/")


@lru_cache
def get_oidc_client():
    if not settings.OIDC_CLIENT_ID or not settings.OIDC_CLIENT_SECRET:
        msg = "Set OIDC_CLIENT_ID and OIDC_CLIENT_SECRET before using OIDC login."
        raise ImproperlyConfigured(msg)

    return oauth.register(
        name="oidc",
        client_id=settings.OIDC_CLIENT_ID,
        client_secret=settings.OIDC_CLIENT_SECRET,
        client_kwargs={"scope": settings.OIDC_SCOPES},
        server_metadata_url=f"{_issuer_url()}/.well-known/openid-configuration",
    )


def callback_url(request):
    return request.build_absolute_uri(reverse("oidc_callback"))


def logout_url(request):
    return request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL)


def provider_logout_url(request, id_token=None):
    client = get_oidc_client()
    metadata = client.load_server_metadata()
    end_session_endpoint = metadata.get("end_session_endpoint")
    return_to = logout_url(request)

    if end_session_endpoint:
        query = {"post_logout_redirect_uri": return_to}
        if id_token:
            query["id_token_hint"] = id_token
        return f"{end_session_endpoint}?{urlencode(query)}"

    query = {
        "client_id": settings.OIDC_CLIENT_ID,
        "returnTo": return_to,
    }
    return f"{_issuer_url()}/v2/logout?{urlencode(query, quote_via=quote_plus)}"


def groups_from_claims(claims):
    groups = claims.get(settings.OIDC_GROUPS_CLAIM, [])
    if isinstance(groups, str):
        return [groups]
    if groups is None:
        return []
    return list(groups)


def user_has_admin_group(user):
    admin_groups = set(settings.OIDC_ADMIN_GROUPS)
    if not admin_groups:
        return False

    try:
        identity = user.oidc_identity
    except ObjectDoesNotExist:
        return False

    return bool(admin_groups.intersection(identity.groups))


def username_from_claims(claims):
    email = claims.get("email", "")
    username = slugify(email.split("@", maxsplit=1)[0]).replace("-", "_")[:150]
    if not username:
        msg = "OIDC claims did not include a usable email username."
        raise ImproperlyConfigured(msg)
    return username


def find_existing_user(user_model, subject, email, username):
    identity = (
        UserIdentity.objects.select_related("user").filter(subject=subject).first()
    )
    if identity:
        return identity.user

    if email:
        user = user_model.objects.filter(email__iexact=email).first()
        if user:
            return user

    return user_model.objects.filter(username=username).first()


def create_user_from_claims(user_model, claims, username):
    email = claims.get("email", "")
    full_name = claims.get("name", "")
    given_name = claims.get("given_name", "")
    family_name = claims.get("family_name", "")

    user = user_model(username=username, email=email)
    user.first_name = given_name or full_name.split(" ", maxsplit=1)[0]
    user.last_name = family_name or (
        full_name.split(" ", maxsplit=1)[1] if " " in full_name else ""
    )
    user.set_unusable_password()
    user.save()
    return user


def ensure_oidc_user_has_unusable_password(user):
    if user.is_staff or user.is_superuser or not user.has_usable_password():
        return

    user.set_unusable_password()
    user.save(update_fields=["password"])


def sync_user_from_claims(claims):
    subject = claims.get("sub")
    if not subject:
        msg = "OIDC claims did not include a subject."
        raise ImproperlyConfigured(msg)

    user_model = get_user_model()
    email = claims.get("email", "")
    username = username_from_claims(claims)
    user = find_existing_user(user_model, subject, email, username)

    if user is None:
        user = create_user_from_claims(user_model, claims, username)
    else:
        ensure_oidc_user_has_unusable_password(user)

    groups = groups_from_claims(claims)
    UserIdentity.objects.update_or_create(
        subject=subject,
        defaults={
            "user": user,
            "groups": groups,
            "claims": dict(claims),
        },
    )
    return user

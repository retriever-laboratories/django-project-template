from unittest.mock import patch
from urllib.parse import parse_qs
from urllib.parse import urlsplit

from authlib.integrations.base_client.errors import MismatchingStateError
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import Group
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test import override_settings

from .auth import OIDCClient
from .auth import user_has_admin_group
from .models import User


@override_settings(OIDC_ADMIN_GROUPS=["admins"])
class OIDCAdminTests(TestCase):
    def test_admin_access__anonymous(self):
        for path in ("/admin/", "/admin/login/", "/admin/users/user/"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 302)
                self.assertEqual(urlsplit(response.url).path, "/login/")

    def test_admin_access__groups(self):
        user = User.objects.create_user("member", subject="auth0|member")
        user.groups.add(Group.objects.create(name="admins"))
        self.client.force_login(user)
        self.assertEqual(self.client.get("/admin/login/").status_code, 200)
        user.groups.clear()
        self.assertEqual(self.client.get("/admin/login/").status_code, 403)
        self.assertEqual(self.client.get("/admin/users/user/").status_code, 403)

    def test_admin_access__local_superuser(self):
        user = User.objects.create_superuser("local", password="secret")
        self.client.force_login(user)
        self.assertEqual(self.client.get("/admin/").status_code, 403)

    @override_settings(OIDC_ADMIN_GROUPS=[])
    def test_admin_access__unconfigured(self):
        user = User.objects.create_user("member", subject="auth0|member")
        user.groups.add(Group.objects.create(name="admins"))
        self.client.force_login(user)
        self.assertEqual(self.client.get("/admin/").status_code, 403)


@override_settings(
    OIDC_GROUPS_CLAIM="groups",
    OIDC_PROVIDER_DOMAIN="tenant.auth0.com",
    OIDC_CLIENT_ID="client",
    OIDC_CLIENT_SECRET="secret",
)
class UserSyncTests(TestCase):
    def setUp(self):
        with patch("users.auth.OAuth"):
            self.oidc = OIDCClient()

    @override_settings(OIDC_GROUPS_CLAIM="https://app.example/groups")
    def test_user_sync__configured_groups_claim(self):
        user = self.oidc._sync_user_from_claims(
            self.claims(
                **{
                    "groups": ["ignored"],
                    "https://app.example/groups": ["operators"],
                }
            )
        )
        self.assertEqual(
            list(user.groups.values_list("name", flat=True)), ["operators"]
        )

    def claims(self, **extra):
        return {"sub": "auth0|123", "email": "user@example.com", **extra}

    def test_user_sync__groups(self):
        user = self.oidc._sync_user_from_claims(
            self.claims(
                **{
                    "groups": ["operators", "operators"],
                }
            )
        )
        self.assertEqual(
            list(user.groups.values_list("name", flat=True)), ["operators"]
        )
        self.assertFalse(user.has_usable_password())
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        local_group = Group.objects.create(name="local")
        user.groups.add(local_group)
        updated = self.oidc._sync_user_from_claims(self.claims())
        self.assertEqual(updated.pk, user.pk)
        self.assertFalse(updated.groups.exists())
        self.assertTrue(Group.objects.filter(pk=local_group.pk).exists())

    def test_user_sync__matching_email(self):
        local = User.objects.create_user("local", email="user@example.com")
        self.assertNotEqual(
            self.oidc._sync_user_from_claims(self.claims()).pk, local.pk
        )

    def test_user_sync__invalid_claims(self):
        for extra in (
            {"sub": ""},
            {"email": []},
        ):
            with self.subTest(extra=extra), self.assertRaises(PermissionDenied):
                self.oidc._sync_user_from_claims(self.claims(**extra))
        self.assertEqual(User.objects.count(), 0)

    def test_user_sync__inactive(self):
        user = User.objects.create_user(
            "disabled", subject="auth0|123", is_active=False
        )
        synced = self.oidc._sync_user_from_claims(self.claims())
        self.assertEqual(synced.pk, user.pk)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_user_sync__existing_password(self):
        user = User.objects.create_user(
            "federated", password="secret", subject="auth0|123"
        )
        self.oidc._sync_user_from_claims(self.claims())
        user.refresh_from_db()
        self.assertFalse(user.has_usable_password())

    @override_settings(OIDC_ADMIN_GROUPS=["admins"])
    def test_admin_group__membership(self):
        user = self.oidc._sync_user_from_claims(
            self.claims(
                **{
                    "groups": ["admins"],
                }
            )
        )
        self.assertTrue(user_has_admin_group(user))
        self.assertFalse(user_has_admin_group(AnonymousUser()))
        user.is_active = False
        self.assertFalse(user_has_admin_group(user))


@override_settings(
    OIDC_PROVIDER_DOMAIN="tenant.auth0.com",
    OIDC_CLIENT_ID="client",
    OIDC_CLIENT_SECRET="secret",
    OIDC_AUDIENCE="api",
)
class OIDCClientTests(TestCase):
    @override_settings(LOGOUT_REDIRECT_URL="/")
    def test_oidc_logout__session(self):
        user = User.objects.create_user("logout-user")
        self.client.force_login(user)
        with patch("users.auth.OAuth"):
            response = self.client.post("/logout/")
        self.assertEqual(response.status_code, 302)
        target = urlsplit(response.url)
        self.assertEqual(target.scheme, "https")
        self.assertEqual(target.netloc, "tenant.auth0.com")
        self.assertEqual(target.path, "/v2/logout")
        self.assertEqual(
            parse_qs(target.query),
            {
                "client_id": ["client"],
                "returnTo": ["http://testserver/"],
            },
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_oidc_logout__get(self):
        self.assertEqual(self.client.get("/logout/").status_code, 405)

    def test_oidc_login__configuration(self):
        with patch("users.auth.OAuth") as oauth:
            client = OIDCClient()
            client.authorize_redirect("request", "https://app.example/login/callback/")
        options = oauth.return_value.register.call_args.kwargs
        self.assertEqual(
            options["server_metadata_url"],
            "https://tenant.auth0.com/.well-known/openid-configuration",
        )
        self.assertEqual(
            options["client_kwargs"]["scope"], "openid profile email groups"
        )
        self.assertEqual(options["client_kwargs"]["code_challenge_method"], "S256")
        oauth.return_value.register.return_value.authorize_redirect.assert_called_once_with(
            "request",
            "https://app.example/login/callback/",
            audience="api",
        )

    def test_oidc_callback__invalid_identity(self):
        with patch("users.auth.OAuth") as oauth:
            client = OIDCClient()
            remote = oauth.return_value.register.return_value
            for token in ({}, {"userinfo": {"iss": "https://other/", "sub": "123"}}):
                remote.authorize_access_token.return_value = token
                with self.subTest(token=token), self.assertRaises(PermissionDenied):
                    client.authenticate("request")
            remote.authorize_access_token.side_effect = MismatchingStateError()
            with self.assertRaises(MismatchingStateError):
                client.authenticate("request")
        self.assertEqual(User.objects.count(), 0)

from django.contrib.auth import get_user_model
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.test import override_settings

from oidc_auth.auth import groups_from_claims
from oidc_auth.auth import sync_user_from_claims
from oidc_auth.auth import user_has_admin_group
from oidc_auth.models import UserIdentity


class LoginRequiredMiddlewareTests(TestCase):
    def test_oidc_login_redirects__admin_index(self):
        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=%2Fadmin%2F")

    def test_oidc_login_redirects__admin_login(self):
        response = self.client.get("/admin/login/")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=%2Fadmin%2Flogin%2F")

    def test_oidc_admin_access__authenticated_user_without_admin_group(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="person",
            email="person@example.com",
        )
        self.client.force_login(user)

        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 403)

    def test_oidc_admin_access__local_superuser_without_admin_group(self):
        user_model = get_user_model()
        user = user_model.objects.create_superuser(
            username="emergency",
            email="emergency@example.com",
            password="local-password",
        )
        self.client.force_login(user)

        response = self.client.get("/admin/login/")

        self.assertEqual(response.status_code, 403)

    @override_settings(OIDC_ADMIN_GROUPS=("django-admins",))
    def test_oidc_admin_access__admin_login_with_admin_group(self):
        user = sync_user_from_claims(
            {
                "sub": "auth0|admin-gate",
                "email": "admin-gate@example.com",
                "groups": ["django-admins"],
            }
        )
        self.client.force_login(user)

        response = self.client.get("/admin/login/")

        self.assertEqual(response.status_code, 200)


class OIDCUserSyncTests(TestCase):
    @override_settings(OIDC_GROUPS_CLAIM="groups")
    def test_oidc_user_sync__new_user(self):
        user = sync_user_from_claims(
            {
                "sub": "auth0|user-123",
                "email": "person@example.com",
                "name": "Person Example",
                "groups": ["engineering", "admins"],
            }
        )

        self.assertEqual(user.username, "person")
        self.assertEqual(user.email, "person@example.com")
        self.assertEqual(user.first_name, "Person")
        self.assertEqual(user.last_name, "Example")
        self.assertFalse(user.has_usable_password())

        identity = UserIdentity.objects.get(user=user)
        self.assertEqual(identity.subject, "auth0|user-123")
        self.assertEqual(identity.groups, ["engineering", "admins"])

    @override_settings(OIDC_GROUPS_CLAIM="https://example.com/groups")
    def test_oidc_groups_from_claims__namespaced_claim(self):
        groups = groups_from_claims({"https://example.com/groups": ["staff"]})

        self.assertEqual(groups, ["staff"])

    def test_oidc_user_sync__existing_staff_user(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="admin",
            email="admin@example.com",
            is_staff=True,
        )

        synced_user = sync_user_from_claims(
            {
                "sub": "auth0|admin",
                "email": "admin@example.com",
                "name": "Admin Example",
                "groups": [],
            }
        )

        self.assertEqual(synced_user.pk, user.pk)
        self.assertTrue(synced_user.is_staff)

    def test_oidc_user_sync__existing_username(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="person",
            email="old@example.com",
            password="local-password",
        )

        synced_user = sync_user_from_claims(
            {
                "sub": "auth0|person",
                "email": "person@example.com",
                "name": "Person Example",
                "groups": [],
            }
        )

        self.assertEqual(synced_user.pk, user.pk)
        self.assertEqual(synced_user.username, "person")
        self.assertEqual(synced_user.email, "old@example.com")
        self.assertFalse(synced_user.has_usable_password())

    def test_oidc_user_sync__missing_email_username(self):
        with self.assertRaises(ImproperlyConfigured):
            sync_user_from_claims(
                {
                    "sub": "auth0|missing-email",
                    "groups": [],
                }
            )

    def test_oidc_user_sync__existing_staff_password(self):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username="admin",
            email="admin@example.com",
            password="local-password",
            is_staff=True,
        )

        synced_user = sync_user_from_claims(
            {
                "sub": "auth0|admin",
                "email": "admin@example.com",
                "groups": [],
            }
        )

        self.assertEqual(synced_user.pk, user.pk)
        self.assertTrue(synced_user.has_usable_password())

    @override_settings(OIDC_ADMIN_GROUPS=("django-admins",))
    def test_oidc_admin_group_check__matching_group(self):
        user = sync_user_from_claims(
            {
                "sub": "auth0|admin-group",
                "email": "admin-group@example.com",
                "groups": ["engineering", "django-admins"],
            }
        )

        self.assertTrue(user_has_admin_group(user))

    @override_settings(OIDC_ADMIN_GROUPS=("django-admins",))
    def test_oidc_admin_group_check__non_matching_group(self):
        user = sync_user_from_claims(
            {
                "sub": "auth0|non-admin-group",
                "email": "non-admin-group@example.com",
                "groups": ["engineering"],
            }
        )

        self.assertFalse(user_has_admin_group(user))

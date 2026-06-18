from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.conf import settings


TEST_STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


class HealthTests(SimpleTestCase):
    def test_health_endpoint_returns_ok(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class SamlSettingsTests(SimpleTestCase):
    def test_idp_metadata_uses_generic_saml_setting(self):
        remote_metadata = settings.SAML_CONFIG["metadata"]["remote"]

        self.assertEqual(remote_metadata[0]["url"], settings.SAML_IDP_METADATA_URL)


@override_settings(STORAGES=TEST_STORAGES)
class LoginRequiredMiddlewareTests(TestCase):
    def test_home_redirects_anonymous_users_to_saml_login(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/saml2/login/?next=/")

    def test_home_allows_authenticated_users(self):
        user = get_user_model().objects.create_user(username="testuser")

        self.client.force_login(user)
        session = self.client.session
        session["saml_roles"] = ["app-admin", "app-user"]
        session.save()
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser")
        self.assertContains(response, "app-admin")
        self.assertContains(response, "app-user")
        self.assertContains(response, "/saml2/logout/")
        self.assertContains(response, 'hx-boost="false"')

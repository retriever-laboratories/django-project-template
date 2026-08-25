from django.test import TestCase
from django.urls import reverse


class HealthTests(TestCase):
    def test_health_endpoint__status(self):
        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


class LoginRequiredTests(TestCase):
    def test_oidc_login_redirects__home(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/login/?next=%2F")

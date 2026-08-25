from django.conf import settings
from django.db import models


class UserIdentity(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="oidc_identity",
    )
    subject = models.CharField(max_length=255, unique=True)
    groups = models.JSONField(default=list, blank=True)
    claims = models.JSONField(default=dict, blank=True)
    last_login_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "user identities"

    def __str__(self):
        return self.subject

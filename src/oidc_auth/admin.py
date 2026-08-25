from django.contrib import admin

from oidc_auth.models import UserIdentity


@admin.register(UserIdentity)
class UserIdentityAdmin(admin.ModelAdmin):
    list_display = ("user", "subject", "last_login_at")
    search_fields = ("user__username", "user__email", "subject")
    readonly_fields = ("created_at", "updated_at", "last_login_at")

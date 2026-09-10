from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class UsersConfig(AppConfig):
    name = "users"


class Admin(AdminConfig):
    # Only activate when explicitly selected as the admin app configuration.
    default = False
    default_site = "users.admin_site.AdminSite"

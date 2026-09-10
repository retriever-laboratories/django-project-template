from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("login/", views.oidc_login, name="login"),
    path("login/callback/", views.oidc_callback, name="callback"),
    path("logout/", views.oidc_logout, name="logout"),
]

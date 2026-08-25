from django.urls import path

from oidc_auth import views

urlpatterns = [
    path("login/", views.login, name="oidc_login"),
    path("login/callback/", views.callback, name="oidc_callback"),
    path("logout/", views.logout, name="oidc_logout"),
]

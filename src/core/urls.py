from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from . import views

def health(_):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    path("", views.index, name="dashboard"),
    # Admin site
    path("admin/", admin.site.urls),

    # Global endpoints
    path("health/", health, name="health"),
]

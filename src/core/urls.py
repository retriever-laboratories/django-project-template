from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path

from core import views

def health(_):
    return JsonResponse({"status": "ok"})

urlpatterns = [
    # Admin site
    path("admin/", admin.site.urls),

    # Global endpoints
    path("health/", health, name="health"),
    path("table/", views.table, name="table"),
]

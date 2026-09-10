from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path
from django.views.decorators.http import require_POST


def health(_):
    return JsonResponse({"status": "ok"})


@require_POST
def ping(request):
    return render(request, "partials/ping_result.html", {"ok": True})


def db_ping(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()[0]
    except Exception as exc:
        return render(
            request,
            "partials/db_ping_result.html",
            {"ok": False, "error": str(exc)},
            status=500,
        )

    return render(
        request,
        "partials/db_ping_result.html",
        {"ok": True, "result": result},
    )


urlpatterns = [
    path("health/", health, name="health"),
    path("db-ping/", db_ping, name="db_ping"),
    path("ping/", ping, name="ping"),
]

# django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

# views
from core import views as core_views


urlpatterns = [
    # Admin site
    path("admin/", admin.site.urls),
    # Global endpoints
    path("", core_views.home, name="home"),
    path("health/", core_views.health, name="health"),
    path("db-ping/", core_views.db_ping, name="db_ping"),
    path("ping/", core_views.ping, name="ping"),
]


if settings.DEBUG:
    from debug_toolbar.toolbar import debug_toolbar_urls

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += debug_toolbar_urls()

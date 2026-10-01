from django.urls import path

from storage_account import views

app_name = "storage_account"

urlpatterns = [
    path("upload/", views.upload_file, name="upload"),
    path("download/", views.download_file, name="download"),
]

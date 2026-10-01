import logging
from pathlib import PurePosixPath
# azure
from azure.core.exceptions import ResourceNotFoundError

# django
from django.core.exceptions import SuspiciousFileOperation
from django.http import FileResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST

# storage account
from storage_account.backends import AzureBlobStorage
from storage_account.models import ExampleModel

logger = logging.getLogger(__name__)

# Demo views for the home-page storage controls, using ExampleModel for uploads.
# Production apps use AzureBlobStorage on their own FileFields and handle
# uploads/downloads in their own views or services.


@require_POST
def upload_file(request):
    uploaded_file = request.FILES.get("file")
    context = {}
    if uploaded_file is None:
        context["error"] = "Choose a file to upload."
    else:
        example = ExampleModel()
        try:
            example.file.save(uploaded_file.name, uploaded_file, save=False)
        except SuspiciousFileOperation:
            context["error"] = "Invalid filename."
        except Exception:
            logger.exception("Storage test upload failed.")
            context["error"] = "Upload failed. Please try again."
        else:
            context["saved_path"] = example.file.name
    return render(request, "storage_account/partials/result.html", context)


@require_GET
def download_file(request):
    path = request.GET.get("path", "")
    try:
        file = AzureBlobStorage().open(path, "rb")
    except ResourceNotFoundError:
        return HttpResponse("File not found.", status=404)
    except Exception:
        logger.exception("Storage test download failed.")
        return HttpResponse("Download failed. Please try again.", status=502)
    return FileResponse(
        file,
        as_attachment=True,
        filename=PurePosixPath(path).name,
    )

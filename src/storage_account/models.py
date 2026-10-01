from django.db import models

from storage_account.backends import AzureBlobStorage


class ExampleModel(models.Model):
    """Manual testing example; other apps can reuse this FileField pattern."""

    file = models.FileField(
        storage=AzureBlobStorage(),
        upload_to="examples/",
        max_length=1024,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name

"""FileField storage for private Azure blobs."""

from tempfile import SpooledTemporaryFile

from azure.core.exceptions import ResourceNotFoundError
from django.core.files import File
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

from storage_account.client import StorageAccountClient


@deconstructible
class AzureBlobStorage(Storage):
    """Connect only during file operations, never during model imports."""

    def _save(self, name, content):
        with StorageAccountClient() as client:
            client.upload(
                name,
                content,
                content_type=getattr(content, "content_type", None),
            )
        return name

    def _open(self, name, mode="rb"):
        if mode != "rb":
            raise ValueError("Only binary read mode is supported.")
        temporary = SpooledTemporaryFile(max_size=8 * 1024 * 1024, mode="w+b")
        try:
            with StorageAccountClient() as client:
                client.download(name).readinto(temporary)
            temporary.seek(0)
            return File(temporary, name=name)
        except Exception:
            temporary.close()
            raise

    def exists(self, name):
        with StorageAccountClient() as client:
            return client.exists(name)

    def size(self, name):
        with StorageAccountClient() as client:
            return client.size(name)

    def delete(self, name):
        with StorageAccountClient() as client:
            try:
                client.delete(name)
            except ResourceNotFoundError:
                pass

    def url(self, name):  # noqa: ARG002
        raise NotImplementedError("Private files require an authorized download view.")

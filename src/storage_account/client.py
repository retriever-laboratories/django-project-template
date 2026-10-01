"""Entra-authenticated client for the configured Azure Blob container."""

from azure.identity import ChainedTokenCredential
from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContentSettings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class StorageAccountClient:
    def __init__(self):
        account_url = settings.AZURE_STORAGE_ACCOUNT_URL
        self.container = settings.AZURE_STORAGE_CONTAINER
        if not account_url or not self.container:
            raise ImproperlyConfigured(
                "Configure AZURE_STORAGE_ACCOUNT_URL and AZURE_STORAGE_CONTAINER."
            )

        self.credential = ChainedTokenCredential(
            ManagedIdentityCredential(),
            DefaultAzureCredential(exclude_managed_identity_credential=True),
        )
        self.client = BlobServiceClient(
            account_url=account_url,
            credential=self.credential,
        )

    def _blob(self, path):
        if not isinstance(path, str) or not path.strip():
            raise ValueError("A non-empty blob path is required.")
        return self.client.get_blob_client(container=self.container, blob=path)

    def upload(self, path, file, *, overwrite=False, content_type=None):
        """Upload a binary stream at its current position; return upload metadata."""
        options = {}
        if content_type:
            options["content_settings"] = ContentSettings(content_type=content_type)
        result = self._blob(path).upload_blob(file, overwrite=overwrite, **options)
        return {"path": path, **result}

    def download(self, path):
        """Return a downloader; consume it before closing this client."""
        return self._blob(path).download_blob()

    def delete(self, path):
        """Delete a blob; propagate storage errors to the caller."""
        self._blob(path).delete_blob()

    def close(self):
        try:
            self.client.close()
        finally:
            self.credential.close()

    def exists(self, path):
        return self._blob(path).exists()

    def size(self, path):
        return self._blob(path).get_blob_properties().size

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):  # noqa: ARG002
        self.close()

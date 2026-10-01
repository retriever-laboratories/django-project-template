# Storage account client

Configure `AZURE_STORAGE_ACCOUNT_URL` and `AZURE_STORAGE_CONTAINER` for an
existing container. Grant the App Service system-assigned managed identity
Storage Blob Data Contributor access.

Authentication tries managed identity, then DefaultAzureCredential with its
managed identity attempt excluded. No authentication-mode setting is required.
Unavailable credentials allow fallback; storage permission failures do not.
Local developer credentials must be accessible where Django runs; a host Azure
CLI login is not automatically available inside Docker.

```python
from storage_account.client import StorageAccountClient

with StorageAccountClient() as storage:
    metadata = storage.upload("documents/report.pdf", uploaded_file)
    storage.download("documents/report.pdf").readinto(destination)
```

Paths are exact blob names inside the configured container. Upload reads a
binary stream from its current position. `overwrite=False` prevents replacement;
`overwrite` and `content_type` are keyword-only options.

Download returns an Azure downloader with `chunks()`, `readinto()`, and
`readall()`. Consume it before closing the client. Streaming HTTP responses must
keep the client open until response iteration finishes.

`delete(path)` supports caller-managed cleanup. SDK exceptions propagate.
Calling apps own authorization, database transactions, and compensation;
database rollback does not undo blob operations.

## FileField example

`ExampleModel` demonstrates using `AzureBlobStorage` without changing the
project's default storage. `upload_to="examples/"` is a prefix; callers supply
the remaining path and blob filename when saving:

```python
from storage_account.models import ExampleModel

example = ExampleModel()
example.file.save("customers/42/report.pdf", uploaded_file, save=False)
# Blob name: examples/customers/42/report.pdf
example.save()

with example.file.open("rb") as file:
    contents = file.read()
```

Do not include the prefix again in `file.save()`. Django validates the relative
path and selects an alternative filename when one already exists. Read
`example.file.name` for the actual saved name. Concurrent upload collisions
raise instead of overwriting an existing blob.

Other apps can use the same backend with their own `upload_to` prefix.
`save=False` skips database persistence, not the upload. Calling apps own atomic
database transactions and explicit cleanup of successfully uploaded blobs if
persistence fails; cleanup failures should be logged and retried. Django does
not automatically delete blobs when records are deleted or files replaced.
Schedule old-file cleanup after the database commit where appropriate.

Downloads use a seekable temporary file, spilling to disk above 8 MiB. The Azure
download completes before `open()` returns. For an authorized download view,
check access to the record, then return `FileResponse(example.file.open("rb"),
as_attachment=True, filename="report.pdf")`; the response closes the file.
Direct `.url`, local `.path`, and text/write opening modes are unsupported.
Default admin file widgets using `.url` need customization for private storage.

`@deconstructible` lets Django serialize the backend's constructor for
migrations; it does not generate migrations or serialize live connections.
No migrations have been generated for ExampleModel. The earlier migration
still describes StorageTestFile and must be reconciled by the developer.

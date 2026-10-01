from io import BytesIO
from unittest.mock import patch

from azure.core.exceptions import HttpResponseError
from azure.core.exceptions import ResourceNotFoundError
from azure.core.exceptions import ServiceRequestError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase
from django.test import override_settings

from storage_account.backends import AzureBlobStorage
from storage_account.client import StorageAccountClient


@override_settings(
    AZURE_STORAGE_ACCOUNT_URL="https://example.blob.core.windows.net",
    AZURE_STORAGE_CONTAINER="documents",
)
class StorageAccountTests(SimpleTestCase):
    def setUp(self):
        self.managed = self.enterContext(
            patch("storage_account.client.ManagedIdentityCredential")
        )
        self.default = self.enterContext(
            patch("storage_account.client.DefaultAzureCredential")
        )
        self.chain = self.enterContext(
            patch("storage_account.client.ChainedTokenCredential")
        )
        self.service = self.enterContext(
            patch("storage_account.client.BlobServiceClient")
        )
        self.blob = self.service.return_value.get_blob_client.return_value
        self.blob.upload_blob.return_value = {}

    def tests_auth(self):
        with StorageAccountClient():
            self.managed.assert_called_once_with()
            self.default.assert_called_once_with(
                exclude_managed_identity_credential=True
            )
            self.chain.assert_called_once_with(
                self.managed.return_value, self.default.return_value
            )

    def tests_destination(self):
        with StorageAccountClient() as client:
            self.service.assert_called_once_with(
                account_url="https://example.blob.core.windows.net",
                credential=self.chain.return_value,
            )
            client.exists("customers/42/report.pdf")
            self.service.return_value.get_blob_client.assert_called_once_with(
                container="documents", blob="customers/42/report.pdf"
            )

    def tests_options(self):
        with StorageAccountClient() as client:
            with self.subTest("defaults"):
                stream = BytesIO(b"report")
                client.upload("report.pdf", stream)
                self.blob.upload_blob.assert_called_once_with(stream, overwrite=False)

            with self.subTest("explicit options"):
                self.blob.upload_blob.reset_mock()
                client.upload(
                    "report.pdf", stream, overwrite=True, content_type="application/pdf"
                )
                args, kwargs = self.blob.upload_blob.call_args
                self.assertEqual(args, (stream,))
                self.assertTrue(kwargs["overwrite"])
                self.assertEqual(
                    kwargs["content_settings"].content_type, "application/pdf"
                )

    def tests_errors(self):
        errors = (
            HttpResponseError("Permission denied."),
            ServiceRequestError("Connection failed."),
        )
        for error in errors:
            with self.subTest("client propagation", error=type(error).__name__):
                self.blob.download_blob.side_effect = error
                with StorageAccountClient() as client:
                    with self.assertRaises(type(error)) as caught:
                        client.download("report.pdf")
                self.assertIs(caught.exception, error)

            with self.subTest("backend propagation", error=type(error).__name__):
                self.blob.delete_blob.side_effect = error
                with self.assertRaises(type(error)) as caught:
                    AzureBlobStorage().delete("report.pdf")
                self.assertIs(caught.exception, error)

        with self.subTest("missing blob deletion"):
            self.blob.delete_blob.side_effect = ResourceNotFoundError("Missing blob.")
            AzureBlobStorage().delete("missing.pdf")

    def tests_close(self):
        for fail in (False, True):
            with self.subTest("operation cleanup", failure=fail):
                self.service.return_value.close.reset_mock()
                self.chain.return_value.close.reset_mock()
                error = ServiceRequestError("Connection failed.")
                self.blob.exists.side_effect = error if fail else None
                if fail:
                    with self.assertRaises(ServiceRequestError):
                        with StorageAccountClient() as client:
                            client.exists("report.pdf")
                else:
                    with StorageAccountClient() as client:
                        client.exists("report.pdf")
                self.service.return_value.close.assert_called_once_with()
                self.chain.return_value.close.assert_called_once_with()

        with self.subTest("credential cleanup when client close fails"):
            self.chain.return_value.close.reset_mock()
            self.service.return_value.close.side_effect = RuntimeError("Close failed.")
            with self.assertRaises(RuntimeError):
                StorageAccountClient().close()
            self.chain.return_value.close.assert_called_once_with()


class BackendTests(SimpleTestCase):
    def setUp(self):
        factory = self.enterContext(
            patch("storage_account.backends.StorageAccountClient")
        )
        self.context = factory.return_value
        self.client = self.context.__enter__.return_value
        self.client.exists.return_value = False
        self.storage = AzureBlobStorage()

    def tests_save(self):
        with self.subTest("success"):
            content = SimpleUploadedFile(
                "report.pdf", b"report", content_type="application/pdf"
            )
            name = self.storage.save("documents/report.pdf", content)
            self.assertEqual(name, "documents/report.pdf")
            self.client.upload.assert_called_once_with(
                name, content, content_type="application/pdf"
            )

        with self.subTest("upload failure"):
            error = ServiceRequestError("Connection failed.")
            self.client.upload.side_effect = error
            self.context.__exit__.reset_mock()
            with self.assertRaises(ServiceRequestError) as caught:
                self.storage.save("documents/report.pdf", content)
            self.assertIs(caught.exception, error)
            self.assertIs(self.context.__exit__.call_args.args[1], error)

    def tests_open(self):
        with self.subTest("success"):
            self.client.download.return_value.readinto.side_effect = (
                lambda destination: destination.write(b"report")
            )
            with self.storage.open("documents/report.pdf") as file:
                self.assertEqual(file.read(), b"report")
                self.assertEqual(file.name, "documents/report.pdf")
            self.assertTrue(file.closed)
            self.client.download.assert_called_once_with("documents/report.pdf")

        for error in (
            ResourceNotFoundError("Missing file."),
            ServiceRequestError("Download interrupted."),
        ):
            with self.subTest("download failure", error=type(error).__name__):
                temporary = BytesIO()
                with patch(
                    "storage_account.backends.SpooledTemporaryFile",
                    return_value=temporary,
                ):
                    self.client.download.side_effect = (
                        error if isinstance(error, ResourceNotFoundError) else None
                    )
                    self.client.download.return_value.readinto.side_effect = error
                    with self.assertRaises(type(error)) as caught:
                        self.storage.open("documents/report.pdf")
                self.assertIs(caught.exception, error)
                self.assertTrue(temporary.closed)

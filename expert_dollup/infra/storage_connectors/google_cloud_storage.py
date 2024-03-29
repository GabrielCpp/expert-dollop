import asyncio
from pathlib import Path
from google.cloud.storage import Client
from google.cloud.exceptions import NotFound
from .storage_client import StorageClient, ObjectNotFound


class GoogleCloudStorage(StorageClient):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = Client()
        self.bucket = self.client.bucket(self.bucket_name)

    async def upload_binary(self, path: str, data: bytes) -> None:
        loop = asyncio.get_event_loop()
        blob = self.bucket.blob(path)
        await loop.run_in_executor(
            None, blob.upload_from_string, data, "application/octet-stream", 3
        )

    async def download_binary(self, path: str) -> bytes:
        loop = asyncio.get_event_loop()
        blob = self.bucket.blob(path)

        try:
            b = await loop.run_in_executor(None, blob.download_as_bytes)
        except NotFound:
            raise ObjectNotFound("Object not found", path=path)

        return b

    @property
    def namespace_prefix(self) -> Path:
        return Path()

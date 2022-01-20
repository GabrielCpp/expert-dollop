import asyncio
from pathlib import Path
from google.auth.credentials import AnonymousCredentials
from google.cloud import storage
from .storage_client import StorageClient


class GoogleCloudStorage(StorageClient):
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        self.client = storage.Client()
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
        b = await loop.run_in_executor(None, blob.download_as_bytes)
        return b

    @property
    def namespace_prefix(self) -> Path:
        return Path()
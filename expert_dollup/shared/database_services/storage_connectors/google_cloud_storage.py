import asyncio
from typing import Optional
from pathlib import Path
from google.cloud.storage import Client
from google.cloud.exceptions import NotFound
from .storage_client import StorageClient, ObjectNotFound, BlobItem
from ..page import Page


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

    async def delete(self, path: str) -> None:
        loop = asyncio.get_event_loop()
        blob = self.bucket.blob(path)
        await loop.run_in_executor(None, blob.delete)

    async def list_by_page(
        self, path: str, page_token: Optional[str] = None
    ) -> Page[BlobItem]:
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None, self.client.list_blobs, self.bucket_name, 1000, page_token, path
        )
        return Page(
            limit=1000,
            results=results,
            next_page_token=results.next_page_token,
            total_count=results.max_results,
        )

    async def exists(self, path: str) -> bool:
        loop = asyncio.get_event_loop()
        blob = self.bucket.blob(path)
        is_existing = await loop.run_in_executor(None, blob.exists)
        return is_existing

    @property
    def namespace_prefix(self) -> Path:
        return Path()

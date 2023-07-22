import asyncio
from tempfile import gettempdir
from pathlib import Path
from shutil import rmtree
from typing import List, Optional
from os import walk, makedirs, fsync
from os.path import join, exists
from dataclasses import dataclass
from .storage_client import StorageClient, ObjectNotFound, BlobItem
from ..page import Page


@dataclass
class FileBlob:
    name: str
    key: str


class LocalStorage(StorageClient):
    def __init__(self, prefix: str):
        self._namespace_prefix = Path(gettempdir()) / prefix
        self._namespace_prefix.mkdir(exist_ok=True)

    async def upload_binary(self, path: str, data: bytes) -> None:
        def run(path, data):
            full_path = self.namespace_prefix / path
            makedirs(full_path.parent, exist_ok=True)

            with open(full_path, "wb") as f:
                f.write(data)
                f.flush()
                fsync(f)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, run, path, data)

    async def download_binary(self, path: str) -> bytes:
        def run():
            full_path = self.namespace_prefix / path

            if not exists(full_path):
                raise ObjectNotFound("Object not found", path=path)

            with open(full_path, "rb") as f:
                return f.read()

        loop = asyncio.get_event_loop()
        b = await loop.run_in_executor(None, run)
        return b

    async def delete(self, path: str) -> None:
        full_path = self.namespace_prefix / path
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, rmtree, full_path, True)

    async def list_by_page(
        self, path: str, page_token: Optional[str] = None
    ) -> Page[BlobItem]:
        def walk_root_folder():
            prefix_root = self.namespace_prefix / path
            results: List[FileBlob] = []
            total_count = 0

            page_reached = False

            for root, _, files in os.walk(prefix_root, topdown=True):
                for name in files:
                    total_count = total_count + 1
                    full_path = join(root, name)

                    if next_page_token is full_path:
                        page_reached = True
                        continue

                    if not next_page_token is None and not page_reached:
                        continue

                    if len(results) >= 1000:
                        continue

                    results.append(FileBlob(name=name, key=full_path))

            return Page(
                limit=1000,
                results=results,
                next_page_token="" if len(results) == 0 else results[-1].key,
                total_count=total_count,
            )

        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(None, walk_root_folder)
        return results

    async def exists(self, path: str) -> bool:
        path = self.namespace_prefix / path
        return exists(path)

    @property
    def namespace_prefix(self) -> Path:
        return self._namespace_prefix

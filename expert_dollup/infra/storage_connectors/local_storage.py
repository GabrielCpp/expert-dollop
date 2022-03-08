import asyncio
from .storage_client import StorageClient
from tempfile import gettempdir
from pathlib import Path
from os import makedirs, fsync
from os.path import exists
from .storage_client import ObjectNotFound


class LocalStorage(StorageClient):
    def __init__(self, prefix: str):
        self.prefix = prefix

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

    @property
    def namespace_prefix(self) -> Path:
        return Path(gettempdir()) / self.prefix

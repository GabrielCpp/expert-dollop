from typing import Callable
from typing import Dict, Type, Callable
from pathlib import Path
from .storage_client import StorageClient


class StorageProxy(StorageClient):
    def __init__(
        self,
        client: StorageClient,
        exception_mappings: Dict[Type, Callable[[Exception], Exception]],
    ):
        self._impl_client = client
        self._exception_mappings = exception_mappings

    async def upload_binary(self, path: str, data: bytes) -> None:
        try:
            await self._impl_client.upload_binary(path, data)
        except Exception as e:
            self._forward_exception(e)

    async def download_binary(self, path: str) -> bytes:
        result: bytes = b""

        try:
            result = await self._impl_client.download_binary(path)
        except Exception as e:
            self._forward_exception(e)

        return result

    @property
    def namespace_prefix(self) -> Path:
        return self._impl_client.namespace_prefix

    def _forward_exception(self, e: Exception) -> None:
        build_error = self._exception_mappings.get(type(e))

        if build_error is None:
            raise

        error = build_error(e)
        raise error from e

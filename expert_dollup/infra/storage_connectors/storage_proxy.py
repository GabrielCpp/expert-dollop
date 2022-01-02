from typing import Callable
from .storage_client import StorageClient
from typing import Dict, Type, Callable


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
        try:
            return await self._impl_client.download_binary(path)
        except Exception as e:
            self._forward_exception(e)

    def _forward_exception(self, e: Exception) -> None:
        build_error = self._exception_mappings.get(type(e))

        if build_error is None:
            raise

        error = build_error(e)
        raise error from e
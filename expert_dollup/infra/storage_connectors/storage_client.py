from abc import ABC, abstractmethod


class StorageClient(ABC):
    @abstractmethod
    async def upload_binary(self, path: str, data: bytes) -> None:
        pass

    @abstractmethod
    async def download_binary(self, path: str) -> bytes:
        pass
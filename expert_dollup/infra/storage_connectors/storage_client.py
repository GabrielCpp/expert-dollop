from abc import ABC, abstractmethod
from pathlib import Path
from expert_dollup.shared.starlette_injection import DetailedError


class ObjectNotFound(DetailedError):
    pass


class StorageClient(ABC):
    @abstractmethod
    async def upload_binary(self, path: str, data: bytes) -> None:
        pass

    @abstractmethod
    async def download_binary(self, path: str) -> bytes:
        pass

    @property
    def namespace_prefix(self) -> Path:
        pass

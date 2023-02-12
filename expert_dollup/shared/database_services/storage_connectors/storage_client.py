from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Protocol
from ..page import Page


class BlobItem(Protocol):
    name: str
    key: str


class ObjectNotFound(Exception):
    def __init__(self, message, **props):
        Exception.__init__(self, message)
        self.props = props

    def __str__(self):
        return f"{Exception.__str__(self)} {self.props}"


class StorageClient(ABC):
    @abstractmethod
    async def upload_binary(self, path: str, data: bytes) -> None:
        pass

    @abstractmethod
    async def download_binary(self, path: str) -> bytes:
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        pass

    @abstractmethod
    async def list_by_page(
        self, path: str, page_token: Optional[str] = None
    ) -> Page[BlobItem]:
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        pass

    @property
    def namespace_prefix(self) -> Path:
        pass

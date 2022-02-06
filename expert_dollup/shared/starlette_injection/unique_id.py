from abc import ABC, abstractmethod
from uuid import UUID, uuid4


class IdProvider(ABC):
    @abstractmethod
    def uuid4(self) -> UUID:
        pass


class UniqueIdGenerator(IdProvider):
    def uuid4(self) -> UUID:
        return uuid4()

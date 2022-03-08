from abc import ABC, abstractmethod
from typing import TypeVar, Generic

Domain = TypeVar("Domain")
ObjectContext = TypeVar("ObjectContext")


class ObjectStorage(ABC, Generic[Domain, ObjectContext]):
    @abstractmethod
    async def save(self, context: ObjectContext, data: Domain) -> None:
        pass

    @abstractmethod
    async def load(self, context: ObjectContext) -> Domain:
        pass

    @abstractmethod
    def get_url(self, context: ObjectContext) -> str:
        pass

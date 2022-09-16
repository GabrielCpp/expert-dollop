from abc import abstractmethod
from typing import Type, TypeVar, Protocol

T = TypeVar("T")


class InjectorProtocol(Protocol):
    @abstractmethod
    def get(self, t: Type[T]) -> T:
        pass

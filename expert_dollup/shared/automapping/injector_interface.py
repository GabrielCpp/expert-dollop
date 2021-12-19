from abc import ABC, abstractmethod
from typing import Type, TypeVar

T = TypeVar("T")


class Injector(ABC):
    @abstractmethod
    def get(self, t: Type[T]) -> T:
        pass

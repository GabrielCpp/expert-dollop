from abc import ABC, abstractmethod
from subprocess import call
from typing import Generic, TypeVar

T = TypeVar("T")
S = TypeVar("S")


class LateBinder(Generic[T, S]):
    @abstractmethod
    def create(self, seed: S) -> T:
        pass


class PureBinding(LateBinder[T, S]):
    def __init__(self, creator: callable):
        self.creator = creator

    def create(self, seed: S) -> T:
        return self.creator(seed)

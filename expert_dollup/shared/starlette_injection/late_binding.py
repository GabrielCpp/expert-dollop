from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Type
from dataclasses import fields
from .injection import Injector

T = TypeVar("T")
S = TypeVar("S")


class LateBinder(ABC, Generic[T, S]):
    @abstractmethod
    def create(self, seed: S) -> T:
        pass


class PureBinding(LateBinder[T, S]):
    def __init__(self, creator: callable):
        self.creator = creator

    def create(self, seed: S) -> T:
        return self.creator(seed)


class DataclassFactory:
    def __init__(self, injector: Injector):
        self._injector = injector

    def __call__(self, f: Type[T]) -> T:
        class_fields = fields(f)
        params = {}

        for class_field in class_fields:
            params[class_field.name] = self._injector.get(class_field.type)

        return f(**params)

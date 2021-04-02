from typing import TypeVar, Generic, Type
from abc import ABC
from injector import Injector

Aggregation = TypeVar("Aggregation")


class Aggregate(Generic[Aggregation]):
    pass


class AggregateFactory:
    def __init__(self, injector: Injector):
        self.injector = injector

    def create(
        class_type: Type[Aggregate[Aggregation]], **kwargs
    ) -> Aggregate[Aggregation]:
        return self.injector.get(class_type).create(**kwargs)

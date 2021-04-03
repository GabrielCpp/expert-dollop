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
        self, class_type: Type[Aggregate[Aggregation]], props: Aggregation
    ) -> Aggregate[Aggregation]:
        return self.injector.get(class_type)._create(props)

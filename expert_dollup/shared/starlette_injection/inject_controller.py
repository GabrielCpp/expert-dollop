from abc import ABC
from typing import TypeVar, Type, Union
from starlette.requests import Request
from logging import Logger


T = TypeVar("T")


class Inject:
    def __init__(self, object_class: Union[ABC, Type[T]]):
        self.object_class = object_class

    def __call__(self, request: Request) -> T:
        container = request.state.container
        assert not container is None, "Container middleware may not be present"

        try:
            return container.get(self.object_class)
        except Exception as e:
            logger = container.get(Logger)
            logger.error(
                f"Fail to inject class {getattr(self.object_class, '__name__', self.object_class)}"
            )
            raise e

from abc import ABC
from typing import TypeVar, Type, Union
from starlette.requests import Request
from logging import Logger
from .injection import Injector

T = TypeVar("T")


class Inject:
    def __init__(self, object_class: Union[ABC, Type[T]]):
        self.object_class = object_class

    def __call__(self, request: Request) -> T:
        injector: Injector = request.state.injector
        assert not injector is None, "Injector middleware may not be present"

        try:
            return injector.get(self.object_class)
        except Exception as e:
            logger = injector.get(Logger)
            logger.error(
                f"Fail to inject class {getattr(self.object_class, '__name__', self.object_class)}"
            )
            raise e

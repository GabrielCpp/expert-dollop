from injector import Injector, Provider
from typing import Type, TypeVar, Callable
from inspect import signature, Parameter

T = TypeVar("T")


class ArgProvider(Provider):
    def __init__(self, type_class: Type[T], kwargs):
        self.type_class = type_class
        self.kwargs = kwargs

    def get(self, injector: Injector) -> T:
        mapped_kwargs = {
            key: injector.get(arg_type) for key, arg_type in self.kwargs.items()
        }
        return self.type_class(**mapped_kwargs)

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, self._callable)


def factory_of(type_class: Type[T], **kwargs):
    sig = signature(type_class.__init__)

    for parameter in sig.parameters.values():
        if not parameter.name in kwargs and parameter.annotation != Parameter.empty:
            kwargs[parameter.name] = parameter.annotation

    return ArgProvider(type_class, kwargs)

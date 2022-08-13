from injector import Injector, Provider
from typing import Type, TypeVar, Callable
from inspect import signature, Parameter

T = TypeVar("T")


class ArgProvider(Provider):
    def __init__(self, type_class: Type[T], kwargs, constants):
        self.type_class = type_class
        self.kwargs = kwargs
        self.constants = constants

    def get(self, injector: Injector) -> T:
        mapped_kwargs = {
            key: injector.get(arg_type) for key, arg_type in self.kwargs.items()
        }
        mapped_kwargs.update(self.constants)
        return self.type_class(**mapped_kwargs)

    def __repr__(self) -> str:
        return "%s(%r)" % (type(self).__name__, self._callable)


class Constant:
    def __init__(self, value):
        self.value = value


def factory_of(type_class: Type[T], **kwargs):
    sig = signature(type_class.__init__)

    for parameter in sig.parameters.values():
        if not parameter.name in kwargs and parameter.annotation != Parameter.empty:
            kwargs[parameter.name] = parameter.annotation

    constants = {}
    for name, parameter in list(kwargs.items()):
        if isinstance(parameter, Constant):
            del kwargs[name]
            constants[name] = parameter.value

    return ArgProvider(type_class, kwargs, constants)

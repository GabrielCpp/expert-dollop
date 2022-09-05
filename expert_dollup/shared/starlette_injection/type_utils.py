from inspect import isclass
from typing import Type, get_args, Union, Callable, Any, Dict
from inspect import signature, Parameter, isclass


def get_classes(m):
    return [class_type for class_type in m.__dict__.values() if isclass(class_type)]


def get_base(class_type: Type) -> Type:
    return class_type.__orig_bases__[0]


def get_arg(class_type: Type, index=0) -> Type:
    return get_args(class_type)[index]


def get_annotations(obj: Union[Callable[..., Any], object]) -> Dict[str, Type]:
    sig = signature(obj.__init__ if isclass(obj) else obj)
    injections: Dict[str, Type] = {}

    for parameter in sig.parameters.values():
        if parameter.name == "self":
            continue

        if parameter.annotation == Parameter.empty:
            raise Exception("Every parameter need a type annotation")

        injections[parameter.name] = parameter.annotation

    return injections

from inspect import isclass
from typing import Type, get_args


def get_classes(m):
    return [class_type for class_type in m.__dict__.values() if isclass(class_type)]


def get_base(class_type: Type) -> Type:
    return class_type.__orig_bases__[0]


def get_arg(class_type: Type, index=0) -> Type:
    return get_args(class_type)[index]

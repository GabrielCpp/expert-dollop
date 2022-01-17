from inspect import isclass


def get_classes(m):
    return [class_type for class_type in m.__dict__.values() if isclass(class_type)]


def get_base(class_type):
    return class_type.__orig_bases__[0]


def get_arg(class_type, index=0):
    return class_type.__args__[index]

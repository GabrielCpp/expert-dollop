from typing import Any


def find_name(elements: list, name: str):
    for element in elements:
        if element.name == name:
            return element

    raise Exception(f"{name} not found")


def to_dict_by_property(elements: list, property_name: str = "name"):
    return {getattr(element, property_name): element for element in elements}


def get_from(d: dict, name: Any):
    result = d[name]
    assert not result is None, f"{name} not in dict"
    return result

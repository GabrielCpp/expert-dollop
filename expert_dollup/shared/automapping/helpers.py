from typing import (
    Tuple,
    Dict,
    Union,
)


def map_dict_keys(
    args: dict, mapping: Dict[str, Tuple[str, Union[None, callable]]]
) -> dict:
    mapped_args = {}

    for (key, value) in args.items():
        if key in mapping:
            (mapped_key, map_value) = mapping[key]
            mapped_args[mapped_key] = value if map_value is None else map_value(value)
        else:
            raise KeyError(f"Key '{key}' not in mapping")

    return mapped_args
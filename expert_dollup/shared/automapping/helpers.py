from dataclasses import dataclass, field
from typing import Callable, Optional, Tuple, Dict, Union, Type, Any, List
from uuid import UUID


@dataclass
class RevervibleMapping:
    from_origin: Dict[Type, Type]
    to_origin: Dict[Type, Type] = field(init=False)

    def __post_init__(self):
        self.to_origin = {
            to_type: from_type for from_type, to_type in self.from_origin.items()
        }


class RevervibleUnionMapping(RevervibleMapping):
    def __init__(
        self,
        origin_union: Any,
        target_union: Any,
        explicit_mapping: Optional[Dict[Type[Any], Type[Any]]] = None,
    ):
        assert getattr(origin_union, "__origin__", None) is Union
        assert getattr(origin_union, "__origin__", None) is Union

        origin_args = getattr(origin_union, "__args__")
        target_args = getattr(target_union, "__args__")
        mappings = explicit_mapping

        if mappings is None:
            assert len(origin_args) == len(target_args)
            mappings = dict(zip(origin_args, target_args))
        else:
            for origin_arg in origin_args:
                assert origin_arg in mappings, f"{origin_arg} not present in mapping"

            mapping_targets = set(mappings.values())
            for target_arg in target_args:
                assert (
                    target_arg in mapping_targets
                ), f"{target_arg} not present in mapping targets"

        RevervibleMapping.__init__(self, mappings)


def map_dict_keys(
    args: dict,
    mapping: Dict[str, Tuple[str, Union[None, Callable[[Any], Any]]]],
    type_of: Optional[str] = None,
    ignore_extra_key=True,
) -> dict:
    mapped_args = {}

    for (key, value) in args.items():
        if key in mapping:
            (mapped_key, map_value) = mapping[key]
            mapped_args[mapped_key] = value if map_value is None else map_value(value)
        elif ignore_extra_key is False:
            raise KeyError(f"Key '{key}' not in mapping")

    if not type_of is None:
        mapped_args["_type"] = type_of

    return mapped_args

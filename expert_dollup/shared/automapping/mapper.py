from typing import Type, TypeVar, Callable, Tuple, Dict, List, Optional, Union
from collections import defaultdict
from inspect import getmembers, isfunction, signature

T = TypeVar("T")
U = TypeVar("U")


class Mapper:
    def __init__(self):
        self._mappings = defaultdict(dict)

    def add_mapping(
        self,
        from_type: Type[T],
        to_type: Type[U],
        mapping_function: Callable[[T, Optional["Mapper"]], U],
    ):
        self._mappings[from_type][to_type] = mapping_function

    def map_many(
        self,
        instances: List[T],
        to_type: Type[U],
        from_type: Type[T] = None,
        after=lambda x: x,
    ) -> List[U]:
        return [after(self.map(instance, to_type, from_type)) for instance in instances]

    def map(self, instance: T, to_type: Type[U], from_type: Type[T] = None) -> U:
        from_type = type(instance) if from_type is None else from_type

        if not from_type in self._mappings:
            raise Exception(f"No mapping for instance {from_type} -> {to_type}")

        submapper = self._mappings.get(from_type)
        object_mapper = submapper.get(to_type)

        if object_mapper is None:
            raise Exception(f"No mapping for target {from_type} -> {to_type}")

        result = object_mapper(instance, self)

        return result

    def add_all_mapper_from_module(self, modules: list) -> "Mapper":
        for module in modules:
            members = getmembers(module)

            for (member_name, *other) in members:
                member = getattr(module, member_name)

                if isfunction(member) and member.__name__.startswith("map_"):
                    sig = signature(member)
                    from_type = next(
                        sig.parameters.values().__iter__(), None
                    ).annotation
                    to_type = sig.return_annotation

                    self.add_mapping(from_type, to_type, member)

        return self

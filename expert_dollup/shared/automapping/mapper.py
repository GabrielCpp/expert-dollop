from typing import Type, TypeVar, Callable, Dict, List, Optional, Union, Any
from collections import defaultdict
from inspect import getmembers, isfunction, signature
from .mapping_error import MapingError
from .injector_interface import Injector


T = TypeVar("T")
U = TypeVar("U")
K = TypeVar("K")


class Mapper:
    def __init__(self, injector: Optional[Injector] = None):
        self._mappings = defaultdict(dict)
        self._injector = injector

    def get(self, class_type: Type[T]) -> T:
        assert not self._injector is None, "Injector not available in mapper."
        return self._injector.get(class_type)

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
        to_type: Union[Type[U], Dict[Type[Any], Type[Any]]],
        from_type: Type[T] = None,
        after=lambda x: x,
    ) -> List[U]:
        return [after(self.map(instance, to_type, from_type)) for instance in instances]

    def map_dict_values(
        self,
        instances: Dict[K, T],
        to_type: Union[Type[U], Dict[Type[Any], Type[Any]]],
        from_type: Type[T] = None,
        after=lambda x: x,
    ) -> Dict[K, U]:
        return {
            key: after(self.map(instance, to_type, from_type))
            for key, instance in instances.items()
        }

    def map_dict_list_values(
        self,
        instances: Dict[K, List[T]],
        to_type: Union[Type[U], Dict[Type[Any], Type[Any]]],
        from_type: Type[T] = None,
        after=lambda x: x,
    ) -> Dict[K, List[U]]:
        return {
            key: after(self.map_many(instance, to_type, from_type))
            for key, instance in instances.items()
        }

    def map(
        self,
        instance: T,
        to_type: Union[Type[U], Dict[Type[Any], Type[Any]]],
        from_type: Type = None,
    ) -> U:
        from_type = type(instance) if from_type is None else from_type

        if isinstance(to_type, dict):
            if not from_type in to_type:
                raise MapingError(
                    f"Mapping for type {str(from_type)} union must be among provided types {','.join(str(t) for t in to_type.keys())}"
                )

            to_type = to_type[from_type]

        if from_type is to_type:
            return instance

        if not from_type in self._mappings:
            raise MapingError(f"No mapping for instance {from_type} -> {to_type}")

        submappers = self._mappings.get(from_type)

        if not to_type in submappers:
            raise MapingError(f"No mapping for target {from_type} -> {to_type}")

        apply_mapping = submappers.get(to_type)
        result = apply_mapping(instance, self)

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

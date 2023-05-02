from abc import abstractmethod
from contextvars import ContextVar
from typing_extensions import TypeAlias
from typing import (
    Type,
    TypeVar,
    Protocol,
    List,
    get_args,
    get_origin,
    Callable,
    Any,
    Generic,
    Union,
    Dict,
    Optional,
)
from dependency_injector.containers import DynamicContainer
from dependency_injector.providers import (
    Singleton,
    Factory,
    AbstractFactory,
    Object,
    Self,
    Callable as CallableFactory,
)


T = TypeVar("T")
ProviderName: TypeAlias = Union[Type, str]


class Provider(Protocol):
    def __call__(self, *args: Any, **kwargs: Any) -> T:
        pass


class Injector(Protocol):
    @abstractmethod
    def get(self, t: Type[T]) -> T:
        pass


ScopedT = TypeVar("ScopedT")
injector_scope: ContextVar[str] = ContextVar("scope", default="")


class Scoped(Generic[ScopedT]):
    def __init__(self, scopes, target):
        self.scopes = scopes
        self.target = target
        self.scope = injector_scope.get()

    @property
    def value(self) -> ScopedT:
        return self.scopes[self.scope][self.target]


class TypedInjection(Injector):
    @staticmethod
    def make_type_name(t: Type, *args: Type) -> str:
        if len(args) == 0:
            return t.__name__

        concat_args = ",".join(TypedInjection.get_type_name(a) for a in args)

        return f"{t.__name__}[{concat_args}]"

    @staticmethod
    def get_type_name(t: Type) -> str:
        origin = get_origin(t)
        args = get_args(t)

        if isinstance(t, list):
            concat_args = ",".join(TypedInjection.get_type_name(a) for a in t)
            return f"[{concat_args}]"

        if origin is None:
            return t.__name__

        concat_args = ",".join(TypedInjection.get_type_name(a) for a in args)
        name = origin.__name__ if hasattr(origin, "__name__") else str(origin)

        return f"{name}[{concat_args}]"

    def __init__(self, container: object, scopes: Dict[str, Dict[str, Any]]):
        self._container = container
        self._scopes = scopes
        self.scope = injector_scope.get()

    def get(self, t: Type[T]) -> T:
        key = TypedInjection.get_type_name(t)
        result = getattr(self._container, key)()
        return result

    def bind_object(self, binded_type: ProviderName, to: Any) -> None:
        setattr(self._container, TypedInjection.get_type_name(binded_type), to)

    def bind_scoped_object(self, binded_type: ProviderName, to: Any):
        self._scopes[self.scope][TypedInjection.get_type_name(binded_type)] = to

    def scoped(self, new_scope: str) -> "TypedInjection":
        self._scopes[new_scope] = {}
        injector_scope.set(new_scope)
        return TypedInjection(self._container, self._scopes)

    def destroy(self):
        del self._scopes[self.scope]

    def clone(self):
        return


class InjectorBuilder:
    @staticmethod
    def forward(obj: Any) -> Provider:
        return Object(obj)

    @staticmethod
    def infer_name(name: ProviderName) -> str:
        if isinstance(name, str):
            return name

        return TypedInjection.get_type_name(name)

    def __init__(self):
        self._scopes = {}
        self._container = DynamicContainer()

    def build(self) -> TypedInjection:
        self._container.check_dependencies()
        return TypedInjection(self._container, self._scopes)

    def add_scoped(self, binded_type: ProviderName) -> None:
        setattr(
            self._container,
            TypedInjection.make_type_name(Scoped, binded_type),
            Factory(
                Scoped,
                scopes=Object(self._scopes),
                target=InjectorBuilder.infer_name(binded_type),
            ),
        )

    def add_container_self(self) -> None:
        setattr(
            self._container,
            InjectorBuilder.infer_name(Injector),
            Factory(
                TypedInjection,
                container=Self(self._container),
                scopes=Object(self._scopes),
            ),
        )

    def add_object(self, binded_type: ProviderName, to: Any) -> None:
        setattr(
            self._container,
            InjectorBuilder.infer_name(binded_type),
            Object(to),
        )

    def add_singleton(
        self, binded_type: ProviderName, to: Type, **kwargs: ProviderName
    ) -> None:
        mapped_kwargs = self._get_providers(kwargs)
        setattr(
            self._container,
            InjectorBuilder.infer_name(binded_type),
            Singleton(to, **mapped_kwargs),
        )

    def add_factory(
        self, binded_type: ProviderName, to: Type[T], **kwargs: ProviderName
    ) -> Callable[[], T]:
        try:
            mapped_kwargs = self._get_providers(kwargs)
        except AttributeError as e:
            raise Exception(f"Faile to inject {to} as {e}") from e

        factory = Factory(to, **mapped_kwargs)

        setattr(
            self._container,
            InjectorBuilder.infer_name(binded_type),
            factory,
        )

        return factory

    def add_abstract_factory(self, binded_type: ProviderName) -> None:
        setattr(
            self._container,
            InjectorBuilder.infer_name(binded_type),
            AbstractFactory(binded_type),
        )

    def override_abstract_factory(
        self, binded_type: ProviderName, to: Type, **kwargs: ProviderName
    ) -> None:
        name = InjectorBuilder.infer_name(binded_type)
        mapped_kwargs = self._get_providers(kwargs)
        factory = Factory(to, **mapped_kwargs)
        getattr(self._container, name).override(factory)

    def _get_providers(
        self, injections: Dict[str, ProviderName]
    ) -> Dict[str, Provider]:
        return {
            name: kawg
            if isinstance(kawg, Object)
            else getattr(self._container, InjectorBuilder.infer_name(kawg))
            for name, kawg in injections.items()
        }

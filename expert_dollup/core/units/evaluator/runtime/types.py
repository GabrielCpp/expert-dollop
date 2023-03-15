from typing import Protocol, Any


class AnyCallable(Protocol):
    def __call__(self, *args, **kwargs) -> Any:
        ...

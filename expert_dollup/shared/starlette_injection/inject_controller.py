from typing import TypeVar, Type
from starlette.requests import Request

T = TypeVar('T')


class Inject:
    def __init__(self, object_class: Type[T]):
        self.object_class = object_class

    def __call__(self, request: Request) -> T:
        container = request.state.container
        assert not container is None, 'Container middleware may not be present'

        return container.get(self.object_class)

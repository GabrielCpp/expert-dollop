import structlog
from typing import TypeVar, Type
from starlette.requests import Request

logger = structlog.get_logger(__name__)

T = TypeVar("T")


class Inject:
    def __init__(self, object_class: Type[T]):
        self.object_class = object_class

    def __call__(self, request: Request) -> T:
        container = request.state.container
        assert not container is None, "Container middleware may not be present"

        try:
            return container.get(self.object_class)
        except Exception as e:
            logger.error(
                f"Fail to inject class {getattr(self.object_class, '__name__', self.object_class)}"
            )
            raise e

from dataclasses import dataclass
from starlette.requests import Request
from .injection import Injector


@dataclass
class GraphqlContext:
    injector: Injector
    request: Request

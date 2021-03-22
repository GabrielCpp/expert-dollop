from dataclasses import dataclass
from injector import Injector
from fastapi import Request


@dataclass
class GraphqlContext:
    container: Injector
    request: Request

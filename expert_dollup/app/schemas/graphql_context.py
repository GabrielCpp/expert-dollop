from dataclasses import dataclass
from injector import Injector


@dataclass
class GraphqlContext:
    container: Injector

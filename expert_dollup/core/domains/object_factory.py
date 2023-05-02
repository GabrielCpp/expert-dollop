from typing import Callable, Type
from dataclasses import dataclass
from typing_extensions import TypeAlias


@dataclass
class ObjectFactory:
    @classmethod
    def create(cls, builder: Callable[[Type["ObjectFactory"]], "ObjectFactory"]):
        return builder(cls)


Instanciator: TypeAlias = Callable[[ObjectFactory], ObjectFactory]

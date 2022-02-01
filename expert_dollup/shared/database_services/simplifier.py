from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

SIMPLIFIERS = {
    UUID: lambda v: str(v),
    Decimal: lambda v: str(v),
}


class Simplifier:
    def __init__(self, simmplifiers=SIMPLIFIERS):
        self._simmplifiers = simmplifiers

    def simplify(self, obj):
        if isinstance(obj, BaseModel):
            return {name: self.simplify(value) for name, value in obj}
        elif isinstance(obj, dict):
            return {name: self.simplify(value) for name, value in obj.items()}
        elif isinstance(obj, list):
            return [self.simplify(value) for value in obj]

        simplify = self._simmplifiers.get(type(obj))

        if simplify is None:
            return obj

        return simplify(obj)

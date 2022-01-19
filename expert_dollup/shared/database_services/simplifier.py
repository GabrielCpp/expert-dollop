from pydantic import BaseModel
from uuid import UUID
from decimal import Decimal

SIMPLIFIERS = {
    UUID: lambda v: str(v),
    Decimal: lambda v: str(v),
}


class Simplifier:
    @staticmethod
    def simplify(obj):
        if isinstance(obj, BaseModel):
            return {name: Simplifier.simplify(value) for name, value in obj}
        elif isinstance(obj, dict):
            return {name: Simplifier.simplify(value) for name, value in obj.items()}
        elif isinstance(obj, list):
            return [Simplifier.simplify(value) for value in obj]

        simplify = SIMPLIFIERS.get(type(obj))

        if simplify is None:
            return obj

        return simplify(obj)

from typing import Type, List, Any
from expert_dollup.shared.database_services import DatabaseContext, batch, QuerySelfByPk
from .schema_core import ConstraintAddContext, ConstraintValidationContext


class CollectionItemExists:
    def __init__(self, db_context: DatabaseContext, domain: Type):
        self.repository = db_context.get_repository(domain)
        self.items = []

    def add(self, context: ConstraintAddContext, value: Any) -> None:
        self.items.append(value)

    async def validate(self, context: ConstraintValidationContext) -> None:
        batch_size = self.repository.batch_size

        for b in batch(self.items, batch_size):
            results = await self.repository.execute(QuerySelfByPk(b))

            if len(results) != len(b):
                context.add_error(len(results), len(b))


class MatchingLength:
    def add(self, context: ConstraintAddContext, target: Any) -> None:
        length = None

        for key in context.arguments:
            value, ok = context.validation_context.access(target, key)

            if not ok:
                raise Exception(f"Target does not has key {key}: {target}")

            if length is None:
                length = len(value)

            if length != len(value):
                context.add_error(length, len(value))

    async def validate(self, context: ConstraintValidationContext) -> None:
        pass


class Unique:
    def __init__(self):
        self.items = set()

    def add(self, context: ConstraintAddContext, target: Any) -> None:
        if target in self.items:
            context.add_error(target, self.items)

        self.items.add(target)

    async def validate(self, context: ConstraintValidationContext) -> None:
        pass


class IdenticalValue:
    def __init__(self):
        self.value = None

    def add(self, context: ConstraintAddContext, target: Any) -> None:
        if self.value is None:
            self.value = target
        elif not (target == self.value):
            context.add_error(target, self.items)

    async def validate(self, context: ConstraintValidationContext) -> None:
        pass

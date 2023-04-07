from typing import Type, List, Any
from expert_dollup.shared.database_services import DatabaseContext, batch, QuerySelfByPk
from .schema_core import (
    ValidationContext,
    ConstraintAddContext,
    ConstraintValidationContext,
)


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
    def add(self, context: ConstraintAddContext, value: Any) -> None:
        length = None

        for key in context.arguments:
            value, ok = context.validation_context.access(value, key)

            if not ok:
                raise Exception()

            if length is None:
                length = len(value)

            if length != len(value):
                context.add_error(len(value), length)

    async def validate(self, context: ConstraintValidationContext) -> None:
        pass

from typing import List
from uuid import UUID
from dataclasses import dataclass
from expert_dollup.core.domains import *
from expert_dollup.core.units import FormulaResolver
from expert_dollup.core.units.evaluator import Unit
from expert_dollup.shared.database_services import Repository


class FormulaUseCase:
    def __init__(
        self,
        formula_service: Repository[Formula],
        formula_resolver: FormulaResolver,
        project_service: Repository[ProjectDetails],
    ):
        self.formula_service = formula_service
        self.formula_resolver = formula_resolver
        self.project_service = project_service

    async def find(self, formula_id: UUID) -> Formula:
        return await self.formula_service.find(formula_id)

    async def add(self, formula_expression: FormulaExpression) -> Formula:
        if await self.formula_service.has(formula_expression.id):
            raise Exception("Formula id already exist")

        formula = await self.formula_resolver.parse(formula_expression)
        await self.formula_service.insert(formula)

        return formula

    async def add_many(self, formula_expressions: List[FormulaExpression]):
        formulas = await self.formula_resolver.parse_many(formula_expressions)
        await self.formula_service.inserts(formulas)

    async def delete(self, formula_id: UUID, remove_recursively: bool):
        await self.formula_service.delete(formula_id)

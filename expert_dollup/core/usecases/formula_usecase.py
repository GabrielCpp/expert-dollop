from typing import List
from uuid import UUID
from expert_dollup.core.domains import *
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.units import FormulaResolver
from expert_dollup.shared.database_services import Repository


class FormulaUseCase:
    def __init__(
        self,
        formula_service: Repository[Formula],
        formula_resolver: FormulaResolver,
        project_service: Repository[ProjectDetails],
        formula_instance_service: ObjectStorage[UnitCache, UnitCacheKey],
    ):
        self.formula_service = formula_service
        self.formula_resolver = formula_resolver
        self.project_service = project_service
        self.formula_instance_service = formula_instance_service

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
        await self.formula_service.find(formula_id)

    async def compute_project_formulas(self, project_id) -> UnitCache:
        project_details = await self.project_service.find(project_id)
        injector = await self.formula_resolver.compute_all_project_formula(
            project_id, project_details.project_definition_id
        )
        instances = injector.unit_instances
        await self.formula_instance_service.save(
            UnitCacheKey(project_id=project_id), instances
        )
        return instances

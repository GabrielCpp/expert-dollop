from typing import List
from uuid import UUID
from expert_dollup.core.domains import (
    Formula,
    FormulaExpression,
    UnitInstanceCache,
    UnitInstanceCacheKey,
)
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.units import FormulaResolver
from expert_dollup.infra.services import (
    FormulaService,
    ProjectService,
)


class FormulaUseCase:
    def __init__(
        self,
        formula_service: FormulaService,
        formula_resolver: FormulaResolver,
        project_service: ProjectService,
        formula_instance_service: ObjectStorage[
            UnitInstanceCache, UnitInstanceCacheKey
        ],
    ):
        self.formula_service = formula_service
        self.formula_resolver = formula_resolver
        self.project_service = project_service
        self.formula_instance_service = formula_instance_service

    async def find_by_id(self, formula_id: UUID) -> Formula:
        return await self.formula_service.find_by_id(formula_id)

    async def add(self, formula_expression: FormulaExpression) -> Formula:
        if await self.formula_service.has(formula_expression.id):
            raise Exception("Formula id already exist")

        formula = await self.formula_resolver.parse(formula_expression)
        await self.formula_service.insert(formula)

        return formula

    async def add_many(self, formula_expressions: List[FormulaExpression]):
        formulas = await self.formula_resolver.parse_many(formula_expressions)
        await self.formula_service.insert_many(formulas)

    async def delete_by_id(self, formula_id: UUID, remove_recursively: bool):
        await self.formula_service.find_by_id(formula_id)

    async def compute_project_formulas(self, project_id) -> UnitInstanceCache:
        project_details = await self.project_service.find_by_id(project_id)
        instances = await self.formula_resolver.compute_all_project_formula(
            project_id, project_details.project_def_id
        )
        await self.formula_instance_service.save(
            UnitInstanceCacheKey(project_id=project_id), instances
        )
        return instances

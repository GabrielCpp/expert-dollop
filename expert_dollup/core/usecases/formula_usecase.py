from uuid import UUID
from typing import Awaitable
from expert_dollup.core.domains import Formula
from expert_dollup.core.units import FormulaResolver
from expert_dollup.infra.services import FormulaService, ProjectService


class FormulaUseCase:
    def __init__(
        self,
        formula_service: FormulaService,
        formula_resolver: FormulaResolver,
        project_service: ProjectService,
    ):
        self.formula_service = formula_service
        self.formula_resolver = formula_resolver
        self.project_service = project_service

    async def find_by_id(self, formula_id: UUID) -> Awaitable[Formula]:
        return await self.formula_service.find_by_id(formula_id)

    async def add(self, formula: Formula) -> Awaitable[Formula]:
        if await self.formula_service.has(formula.id):
            raise Exception()

        await self.formula_service.insert(formula)
        formula_details = await self.formula_resolver.parse(formula)
        await self.formula_service.patch_formula_graph(formula_details)

        return formula

    async def delete_by_id(
        self, formula_id: UUID, remove_recursively: bool
    ) -> Awaitable:
        await self.formula_service.find_by_id(formula_id)

    async def compute_project_formulas(self, project_id) -> Awaitable:
        project = await self.project_service.find_by_id(project_id)
        await self.formula_resolver.compute_all_project_formula(
            project_id, project.project_def_id
        )

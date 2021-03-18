from uuid import UUID
from typing import List
from expert_dollup.shared.database_services import BaseCompositeCrudTableService
from expert_dollup.infra.expert_dollup_db import (
    project_formula_cache_table,
    ProjectFormulaCacheDao,
)
from expert_dollup.core.domains import FormulaCachedResult


class FormulaCacheService(BaseCompositeCrudTableService[FormulaCachedResult]):
    class Meta:
        table = project_formula_cache_table
        dao = ProjectFormulaCacheDao
        domain = FormulaCachedResult
        table_filter_type = None

    async def repopulate(self, project_id: UUID, domains: List[FormulaCachedResult]):
        query = self._table.delete().where(self._table.c.project_id == project_id)
        await self._database.execute(query=query)
        await self.insert_many(domains)

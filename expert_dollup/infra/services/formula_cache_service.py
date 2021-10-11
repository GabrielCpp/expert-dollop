from uuid import UUID
from typing import List
from expert_dollup.shared.database_services import PostgresTableService
from expert_dollup.infra.expert_dollup_db import (
    project_formula_cache_table,
    ProjectFormulaCacheDao,
)
from expert_dollup.core.domains import FormulaCachedResult, FormulaCachedResultFilter


class FormulaCacheService(PostgresTableService[FormulaCachedResult]):
    class Meta:
        table = project_formula_cache_table
        dao = ProjectFormulaCacheDao
        domain = FormulaCachedResult
        table_filter_type = FormulaCachedResultFilter

    async def repopulate(self, project_id: UUID, domains: List[FormulaCachedResult]):
        await self.delete_by(FormulaCachedResultFilter(project_id=project_id))
        await self.insert_many(domains)

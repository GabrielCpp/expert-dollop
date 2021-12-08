from uuid import UUID
from typing import List
from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import ProjectFormulaCacheDao
from expert_dollup.core.domains import FormulaCachedResult, FormulaCachedResultFilter


class FormulaCacheService(CollectionServiceProxy[FormulaCachedResult]):
    class Meta:
        dao = ProjectFormulaCacheDao
        domain = FormulaCachedResult
        table_filter_type = FormulaCachedResultFilter

    async def repopulate(self, project_id: UUID, domains: List[FormulaCachedResult]):
        await self.delete_by(FormulaCachedResultFilter(project_id=project_id))
        await self.insert_many(domains)

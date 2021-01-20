from typing import List, Awaitable, Dict
from uuid import UUID
from sqlalchemy import func, select
from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_definition_plugin_table,
    ProjectDefinitionPluginDao,
)
from expert_dollup.core.domains import ProjectDefinitionPlugin
from expert_dollup.shared.database_services import BaseCrudTableService


class ProjectDefinitionPluginService(BaseCrudTableService[ProjectDefinitionPlugin]):
    class Meta:
        table = project_definition_plugin_table
        dao = ProjectDefinitionPluginDao
        domain = ProjectDefinitionPlugin
        seach_filters = {}

    async def has_every_id(self, ids: List[UUID]) -> Awaitable[bool]:
        if len(ids) == 0:
            return True

        query = (
            select([func.count()])
            .select_from(self._table)
            .where(self._table.c.id.in_(ids))
        )

        count = await self._database.fetch_val(query)

        return count == len(ids)

    async def get_config_validation_schemas(
        self, ids: List[UUID]
    ) -> Awaitable[Dict[str, dict]]:
        if len(ids) == 0:
            return {}

        query = (
            select([self._table.name, self._table.validation_schema])
            .select_from(self._table)
            .where(self._table.c.id.in_(ids))
            .limit(1000)
        )

        elements = await self._database.fetch_all(query)

        return {element.name: element.validation_schema for element in elements}

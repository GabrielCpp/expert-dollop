from typing import List, Dict, Optional
from uuid import UUID
from expert_dollup.core.domains import Formula
from expert_dollup.infra.expert_dollup_db import ProjectDefinitionFormulaDao
from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    InternalRepository,
)


class FormulaInternalRepository(CollectionServiceProxy):
    def __init__(self, repository: InternalRepository[Formula]):
        CollectionServiceProxy.__init__(self, repository)
        self._repository = repository

    async def get_formulas_id_by_name(
        self, project_definition_id: UUID, names: Optional[List[str]] = None
    ) -> Dict[str, UUID]:
        query = (
            self._repository.get_builder()
            .select("id", "name")
            .where("project_definition_id", "==", project_definition_id)
        )

        if not names is None:
            if len(names) == 0:
                return {}

            query = query.where("name", "in", names)

        records = await self._repository.fetch_all_records(query)

        return {record.get("name"): UUID(str(record.get("id"))) for record in records}

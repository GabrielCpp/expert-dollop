from typing import Iterable, Dict, Optional
from uuid import UUID
from expert_dollup.core.domains import Formula
from expert_dollup.infra.expert_dollup_db import ProjectDefinitionFormulaDao
from expert_dollup.shared.database_services import CollectionServiceProxy


class FormulaService(CollectionServiceProxy[Formula]):
    class Meta:
        dao = ProjectDefinitionFormulaDao
        domain = Formula

    async def get_formulas_id_by_name(
        self, project_definition_id: UUID, names: Optional[Iterable[str]] = None
    ) -> Dict[str, UUID]:
        query = (
            self.get_builder()
            .select("id", "name")
            .where("project_definition_id", "==", project_definition_id)
        )

        if not names is None:
            if len(names) == 0:
                return {}

            query = query.where("name", "in", names)

        records = await self.fetch_all_records(query)

        return {record.get("name"): UUID(str(record.get("id"))) for record in records}

from typing import List, Dict, Optional
from uuid import UUID
from expert_dollup.core.domains import Formula, FormulaFilter, FormulaPluckFilter
from expert_dollup.infra.expert_dollup_db import ProjectDefinitionFormulaDao
from expert_dollup.shared.database_services import (
    CollectionServiceProxy,
    IdStampedDateCursorEncoder,
)


class FormulaService(CollectionServiceProxy[Formula]):
    class Meta:
        dao = ProjectDefinitionFormulaDao
        domain = Formula
        paginator = IdStampedDateCursorEncoder.for_fields("name", str, str, "")

    async def get_formulas_id_by_name(
        self, project_def_id: UUID, names: Optional[List[str]] = None
    ) -> Dict[str, UUID]:
        if names is None:
            query = (
                self.get_builder()
                .select_fields("id", "name")
                .find_by(FormulaFilter(project_def_id=project_def_id))
                .finalize()
            )

            records = await self.fetch_all_records(query)

            return {record.get("name"): record.get("id") for record in records}

        if len(names) == 0:
            return {}

        query = (
            self.get_builder()
            .select_fields("id", "name")
            .find_by(FormulaFilter(project_def_id=project_def_id))
            .pluck(FormulaPluckFilter(names=names))
            .finalize()
        )
        records = await self.fetch_all_records(query)

        return {record.get("name"): record.get("id") for record in records}

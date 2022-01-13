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

    async def find_formula_final_ast_by_formula_id(
        self, project_def_id: UUID
    ) -> Dict[UUID, dict]:
        query = (
            self.get_builder()
            .select("id", "final_ast")
            .where("project_def_id", "==", project_def_id)
        )
        records = await self.fetch_all_records(query)

        return {record.get("id"): record.get("final_ast") for record in records}

    async def get_formulas_id_by_name(
        self, project_def_id: UUID, names: Optional[List[str]] = None
    ) -> Dict[str, UUID]:
        query = (
            self.get_builder()
            .select("id", "name")
            .where("project_def_id", "==", project_def_id)
        )

        if not names is None:
            if len(names) == 0:
                return {}

            query = query.where("name", "in", names)

        records = await self.fetch_all_records(query)

        return {record.get("name"): record.get("id") for record in records}

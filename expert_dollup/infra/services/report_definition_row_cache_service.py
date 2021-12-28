from uuid import UUID
from typing import List
from expert_dollup.core.domains import ReportRowDict
from expert_dollup.shared.database_services import JsonSerializer


class ReportDefinitionRowCacheService:
    def __init__(self):
        pass

    async def save(self, report_definition_id: UUID, rows: List[ReportRowDict]):
        with open("./report_rows.json", "w") as f:
            f.write(JsonSerializer.encode(rows))

    async def load(self, report_definition_id: UUID):
        with open("./report_rows.json", "r") as f:
            return JsonSerializer.decode(f.read())
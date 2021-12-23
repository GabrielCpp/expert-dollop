from uuid import UUID
from ..units import ReportLinking


class ReportUseCase:
    def __init__(self, report_linking: ReportLinking):
        self.report_linking = report_linking

    async def get_report_rows(self, project_id: UUID, report_definition_id: UUID):
        await self.report_linking.link_report()
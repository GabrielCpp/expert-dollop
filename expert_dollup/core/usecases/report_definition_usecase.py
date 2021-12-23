from uuid import UUID
from ..units import ReportRowCacheBuilder


class ReportDefinitionUseCase:
    def __init__(self, report_row_cache_builder: ReportRowCacheBuilder):
        self.report_row_cache_builder = report_row_cache_builder

    async def refresh_cache(self, report_definition_id: UUID) -> None:
        await self.report_row_cache_builder.refresh_cache()
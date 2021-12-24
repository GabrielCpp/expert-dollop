from uuid import UUID
from expert_dollup.core.units import ReportRowCacheBuilder
from expert_dollup.infra.services import *


class ReportDefinitionUseCase:
    def __init__(
        self,
        report_definition_service: ReportDefinitionService,
        report_row_cache_builder: ReportRowCacheBuilder,
    ):
        self.report_definition_service = report_definition_service
        self.report_row_cache_builder = report_row_cache_builder

    async def refresh_cache(self, report_definition_id: UUID) -> None:
        report_definition = await self.report_definition_service.find_by_id(
            report_definition_id
        )
        await self.report_row_cache_builder.refresh_cache(report_definition)
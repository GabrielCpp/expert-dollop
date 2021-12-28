from uuid import UUID
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.units import ReportRowCacheBuilder
from expert_dollup.core.domains import *
from expert_dollup.infra.services import *


class ReportDefinitionUseCase:
    def __init__(
        self,
        report_definition_service: ReportDefinitionService,
        report_row_cache_builder: ReportRowCacheBuilder,
        report_definition_row_cache_service: ObjectStorage[
            ReportRowsCache, ReportRowKey
        ],
    ):
        self.report_definition_service = report_definition_service
        self.report_row_cache_builder = report_row_cache_builder
        self.report_definition_row_cache_service = report_definition_row_cache_service

    async def refresh_cache(self, report_definition_id: UUID) -> None:
        report_definition = await self.report_definition_service.find_by_id(
            report_definition_id
        )
        report_cached_rows = await self.report_row_cache_builder.refresh_cache(
            report_definition
        )
        await self.report_definition_row_cache_service.save(
            ReportRowKey(
                project_def_id=report_definition.project_def_id,
                report_definition_id=report_definition_id,
            ),
            report_cached_rows,
        )

    async def add(self, report_definition: ReportDefinition):
        await self.report_definition_service.insert(report_definition)

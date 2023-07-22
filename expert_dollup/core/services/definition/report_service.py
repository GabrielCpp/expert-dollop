from re import I
from uuid import UUID
from typing import List
from expert_dollup.core.units import ReportRowCache
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import Repository


class ReportDefinitionUseCase:
    def __init__(
        self,
        report_definition_service: Repository[ReportDefinition],
        report_row_cache_builder: ReportRowCache,
        report_definition_row_cache_service: Repository[CompiledReport],
    ):
        self.report_definition_service = report_definition_service
        self.report_row_cache_builder = report_row_cache_builder
        self.report_definition_row_cache_service = report_definition_row_cache_service

    async def refresh_cache(self, report_definition_id: UUID) -> None:
        report_definition = await self.report_definition_service.find(
            report_definition_id
        )
        report_cached_rows = await self.report_row_cache_builder.refresh_cache(
            report_definition
        )
        await self.report_definition_row_cache_service.insert(
            CompiledReport(
                CompiledReportKey(
                    project_definition_id=report_definition.project_definition_id,
                    id=report_definition_id,
                ),
                structure=report_definition.structure,
                name=report_definition.name,
                rows=report_cached_rows,
            )
        )

    async def add(self, report_definition: ReportDefinition):
        await self.report_definition_service.insert(report_definition)

    async def find_all_reports_definitions(
        self, project_definition_id: UUID
    ) -> List[ReportDefinition]:
        report_definitions = await self.report_definition_service.find_by(
            ReportDefinitionFilter(project_definition_id=project_definition_id)
        )
        return report_definitions

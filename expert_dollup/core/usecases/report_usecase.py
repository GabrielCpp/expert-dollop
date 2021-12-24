from uuid import UUID
from typing import List
from expert_dollup.core.domains import (
    ReportRow,
    ReportDefinitionFilter,
    ReportDefinition,
)
from expert_dollup.core.units import ReportLinking
from expert_dollup.infra.services import *


class ReportUseCase:
    def __init__(
        self,
        report_definition_service: ReportDefinitionService,
        project_service: ProjectService,
        report_linking: ReportLinking,
    ):
        self.report_definition_service = report_definition_service
        self.project_service = project_service
        self.report_linking = report_linking

    async def get_avaible_reports(self, project_id: UUID) -> List[ReportDefinition]:
        project_details = await self.project_service.find_by_id(project_id)
        report_definitions = await self.report_definition_service.find_by(
            ReportDefinitionFilter(project_def_id=project_details.project_def_id)
        )

        return report_definitions

    async def get_report_rows(
        self, project_id: UUID, report_definition_id: UUID
    ) -> List[ReportRow]:
        project_details = await self.project_service.find_by_id(project_id)
        report_definition = await self.report_definition_service.find_by_id(
            report_definition_id
        )
        report_rows = await self.report_linking.link_report(
            report_definition, project_details
        )
        return report_rows
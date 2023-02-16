from typing import List
from uuid import UUID
from expert_dollup.core.domains import *
from expert_dollup.core.units import ReportLinking
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.shared.database_services import Repository


class ReportUseCase:
    def __init__(
        self,
        report_definition_service: Repository[ReportDefinition],
        project_service: Repository[ProjectDetails],
        report_linking: ReportLinking,
        report_storage: ObjectStorage[Report, ReportKey],
    ):
        self.report_definition_service = report_definition_service
        self.project_service = project_service
        self.report_linking = report_linking
        self.report_storage = report_storage

    async def get_report(
        self, project_id: UUID, report_definition_id: UUID, save_report: bool = False
    ) -> Report:
        project_details = await self.project_service.find(project_id)
        report_definition = await self.report_definition_service.find(
            report_definition_id
        )
        report = await self.report_linking.link_report(
            report_definition, project_details
        )

        if save_report:
            await self.report_storage.save(
                ReportKey(
                    project_id=project_id, report_definition_id=report_definition_id
                ),
                report,
            )

        return report

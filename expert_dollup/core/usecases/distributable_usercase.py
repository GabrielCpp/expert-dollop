from typing import List
from uuid import UUID
from expert_dollup.core.domains import *
from expert_dollup.core.units import *
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.shared.database_services import CollectionService


class DistributableUseCase:
    def __init__(
        self,
        distributable_service,
        report_distributor: ReportDistributor,
        report_definition_service: CollectionService[ReportDefinition],
        project_service: CollectionService[ProjectDetails],
        report_linking: ReportLinking,
        report_storage: ObjectStorage[Report, ReportKey],
    ):
        self.distributable_service = distributable_service
        self.report_distributor = report_distributor
        self.report_definition_service = report_definition_service
        self.project_service = project_service
        self.report_linking = report_linking
        self.report_storage = report_storage

    async def distributable_reports(self, project_id: UUID) -> List[ReportDefinition]:
        project_details = await self.project_service.find_by_id(project_id)
        report_definitions = await self.report_definition_service.find_by(
            ReportDefinitionFilter(
                project_definition_id=project_details.project_definition_id,
                distributable=True,
            )
        )

        return report_definitions

    async def distribute(
        self,
        project_id: UUID,
        report_definition_id: UUID,
        items: List[UUID],
    ) -> Distributable:
        distributable = await self.distributable_service.find_by_id(
            DistributableId(
                project_id=project_id, report_definition_id=report_definition_id
            )
        )
        distributable = self.report_distributor.distribute(distributable, items)
        await self.distributable_service.upserts([distributable])
        return distributable

    async def update_distributable(
        self, project_id: UUID, report_definition_id: UUID
    ) -> Distributable:
        project_details = await self.project_service.find_by_id(project_id)
        report_definition = await self.report_definition_service.find_by_id(
            report_definition_id
        )
        report = await self.report_linking.link_report(
            report_definition, project_details
        )
        await self.report_storage.save(
            ReportKey(project_id=project_id, report_definition_id=report_definition_id),
            report,
        )
        distributable = await self.distributable_service.find_by_id(
            DistributableId(
                project_id=project_id, report_definition_id=report_definition_id
            )
        )
        self.report_distributor.update_from_report(
            distributable, report, report_definition
        )
        await self.distributable_service.upserts([distributable])

        return distributable

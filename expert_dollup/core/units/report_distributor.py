from typing import Dict, List
from uuid import UUID, uuid4
from expert_dollup.core.domains import *
from expert_dollup.shared.starlette_injection import Clock
from expert_dollup.shared.database_services import DatabaseContext


class ReportDistributor:
    def __init__(self, clock: Clock, database_context: DatabaseContext):
        self.clock = clock
        self.database_context = database_context

    async def update_from_report(
        self,
        report_key: ReportKey,
        report: Report,
        distributable_items: List[DistributableItem],
    ) -> DistributableUpdate:
        newer_items: Dict[str, DistributableItem] = {}
        obsolete_distributions = set()
        child_reference_ids = self._get_child_reference_ids(report)
        organization_by_ids = await self._get_organization_id_by_child_reference(
            report.datasheet_id, child_reference_ids
        )

        for stage in report.stages:
            for row in stage.rows:
                item = DistributableItem(
                    project_id=report_key.project_id,
                    report_definition_id=report_key.report_definition_id,
                    node_id=row.node_id,
                    formula_id=row.formula_id,
                    supplied_item=SuppliedItem(
                        datasheet_id=report.datasheet_id,
                        aggregate_id=row.aggregate_id,
                        element_id=row.element_id,
                        organization_id=organization_by_ids[row.element_id],
                    ),
                    distribution_ids=[],
                    summary=stage.summary,
                    columns=row.columns,
                    obsolete=False,
                    creation_date_utc=self.clock.utcnow(),
                )

                newer_items[item.id] = item

        for item in distributable_items:
            if item.id in newer_items:
                newer_item = newer_items[item.id]
                newer_item.distribution_ids = item.distribution_ids
                newer_item.obsolete = False

                if newer_item.columns != item.columns:
                    obsolete_distributions.update(item.distribution_ids)
            else:
                item.obsolete = True
                newer_items[item.id] = item
                obsolete_distributions.update(item.distribution_ids)

        return DistributableUpdate(
            items=list(newer_items.values()),
            obsolete_distribution_ids=list(obsolete_distributions),
        )

    def distribute(self, distributable_items: List[DistributableItem]) -> Distribution:
        distribution_id = uuid4()
        distribution = Distribution(
            id=distribution_id,
            file_url="",
            item_ids=[item.id for item in distributable_items],
            state=DistributionState.PENDING,
            obsolete=False,
            creation_date_utc=self.clock.utcnow(),
        )

        return distribution

    def _get_child_reference_ids(self, report: Report) -> List[UUID]:
        reference_ids = []

        for stage in report.stages:
            for row in stage.rows:
                reference_ids.append(row.element_id)

        return reference_ids

    async def _get_organization_id_by_child_reference(
        self, datasheet_id: UUID, child_reference_ids: List[UUID]
    ):
        report_datasheet_elements = await self.database_context.execute(
            DatasheetElement,
            DatasheetElementPluckFilter(
                datasheet_id=datasheet_id, child_element_references=child_reference_ids
            ),
        )
        organization_by_ids = {
            element.child_element_reference: element.original_owner_organization_id
            for element in report_datasheet_elements
        }

        return organization_by_ids

from dataclasses import dataclass
from typing import Dict
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.shared.starlette_injection import Clock


@dataclass
class DistributableReportItem(DistributableItem):
    summary: ComputedValue
    obsolete: bool


class ReportDistributor:
    def __init__(self, clock: Clock):
        self.clock = clock

    def update_from_report(
        self,
        distributable: Distributable,
        report: Report,
        report_definition: ReportDefinition,
    ):
        newer_items: Dict[str, DistributableReportItem] = {}
        column_names = [c.name for c in report_definition.structure.columns]

        for stage in report.stages:
            for row in stage.rows:
                item = DistributableReportItem(
                    distribution_ids=[],
                    node_id=row.node_id,
                    formula_id=row.formula_id,
                    element_def_id=row.element_def_id,
                    columns=dict(zip(column_names, row.columns)),
                    summary=stage.summary,
                    obsolete=False,
                )

                newer_items[item.id] = item

        for group in distributable.groups:
            for item in group.items:
                if item.id in newer_items:
                    newer_items.distribution_ids = item.distribution_ids
                    newer_items.obsolete = False

                    if newer_items.columns != item.columns:
                        self.flag_distribution_as_obsolete(
                            item.distribution_ids, item.id
                        )
                else:
                    item = DistributableReportItem(
                        distribution_ids=item.distribution_ids,
                        node_id=item.node_id,
                        formula_id=item.formula_id,
                        element_def_id=item.element_def_id,
                        columns=item.columns,
                        summary=group.summary,
                        obsolete=True,
                    )

                    newer_items[item.id] = item

    def distribute(self, distributable: Distributable, items: List[UUID]):
        distribution_id = uuid4()
        distribution = Distribution(
            id=distribution_id,
            creation_date_utc=self.clock.utcnow(),
            item_ids=items,
            state=DistributionState.PENDING,
        )

        distributable.distributions.append(distribution)

        return distributable

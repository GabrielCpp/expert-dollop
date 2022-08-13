from ast import dump
import pytest
from unittest.mock import MagicMock
from uuid import uuid4, UUID
from expert_dollup.core.units import ReportDistributor
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import DatabaseContext, Plucker
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup, AsyncMock
from ....fixtures import *


def make_report() -> Report:
    return ReportFactory(
        stages=[
            ReportStageFactory(
                rows=[
                    ReportRowFactory(
                        columns=[
                            ComputedValueFactory(label="stage", value=1),
                            ComputedValueFactory(
                                label="quantity", value=2, unit="unit"
                            ),
                            ComputedValueFactory(
                                label="product_name", value=3, unit=None
                            ),
                        ]
                    ),
                    ReportRowFactory(
                        columns=[
                            ComputedValueFactory(label="stage", value=4),
                            ComputedValueFactory(
                                label="quantity", value=5, unit="unit"
                            ),
                            ComputedValueFactory(
                                label="product_name", value=6, unit=None
                            ),
                        ]
                    ),
                ]
            )
        ]
    )


@pytest.mark.asyncio
async def test_update_empty_distributable_from_report(static_clock):
    organization_id = uuid4()

    def organization_id_by_child_reference(_, child_reference_ids):
        return {id: organization_id for id in child_reference_ids}

    database_context = StrictInterfaceSetup(DatabaseContext)
    report_distributor = ReportDistributor(static_clock, database_context.object)

    report_key = ReportKeyFactory()
    report = make_report()
    expected_update = DistributableUpdate(
        items=[
            DistributableItem(
                distribution_ids=[],
                project_id=report_key.project_id,
                report_definition_id=report_key.report_definition_id,
                node_id=report.stages[0].rows[0].node_id,
                formula_id=report.stages[0].rows[0].formula_id,
                supplied_item=SuppliedItem(
                    datasheet_id=report.datasheet_id,
                    element_def_id=report.stages[0].rows[0].element_def_id,
                    child_reference_id=report.stages[0].rows[0].child_reference_id,
                    organization_id=organization_id,
                ),
                summary=report.stages[0].summary,
                columns=[
                    ComputedValue(label="stage", value=1, unit="$"),
                    ComputedValue(label="quantity", value=2, unit="unit"),
                    ComputedValue(label="product_name", value=3, unit=None),
                ],
                obsolete=False,
                creation_date_utc=static_clock.utcnow(),
            ),
            DistributableItem(
                distribution_ids=[],
                project_id=report_key.project_id,
                report_definition_id=report_key.report_definition_id,
                node_id=report.stages[0].rows[1].node_id,
                formula_id=report.stages[0].rows[1].formula_id,
                supplied_item=SuppliedItem(
                    datasheet_id=report.datasheet_id,
                    element_def_id=report.stages[0].rows[1].element_def_id,
                    child_reference_id=report.stages[0].rows[1].child_reference_id,
                    organization_id=organization_id,
                ),
                summary=report.stages[0].summary,
                columns=[
                    ComputedValue(label="stage", value=4, unit="$"),
                    ComputedValue(label="quantity", value=5, unit="unit"),
                    ComputedValue(label="product_name", value=6, unit=None),
                ],
                obsolete=False,
                creation_date_utc=static_clock.utcnow(),
            ),
        ],
        obsolete_distribution_ids=[],
    )

    report_distributor._get_organization_id_by_child_reference = AsyncMock(
        side_effect=organization_id_by_child_reference
    )

    distributable_update = await report_distributor.update_from_report(
        report_key, report, []
    )

    assert distributable_update == expected_update

import pytest
from unittest.mock import MagicMock
from uuid import uuid4, UUID
from expert_dollup.core.units import ReportDistributor
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import DatabaseContext, Plucker
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup, AsyncMock
from ....fixtures import *


@pytest.mark.asyncio
async def test_update_empty_distributable_from_report(static_clock):
    project_id = uuid4()
    organization_id = uuid4()
    database_context = StrictInterfaceSetup(DatabaseContext)
    report_distributor = ReportDistributor(static_clock, database_context.object)
    project_details = ProjectDetailsFactory()
    report_definition = ReportDefinitionFactory(distributable=True)
    report = ReportFactory(
        stages=[
            ReportStageFactory(
                rows=[
                    ReportRowFactory(
                        columns=[
                            ComputedValueFactory(value=1),
                            ComputedValueFactory(value=2),
                            ComputedValueFactory(value=3),
                        ]
                    ),
                    ReportRowFactory(
                        columns=[
                            ComputedValueFactory(value=4),
                            ComputedValueFactory(value=5),
                            ComputedValueFactory(value=6),
                        ]
                    ),
                ]
            )
        ]
    )

    def organization_id_by_child_reference(_, child_reference_ids):
        return {id: organization_id for id in child_reference_ids}

    report_distributor._get_organization_id_by_child_reference = AsyncMock(
        side_effect=organization_id_by_child_reference
    )

    distributable_update = await report_distributor.update_from_report(
        project_details, report_definition, report, []
    )
    print(distributable_update)
    assert distributable_update == DistributableUpdate(
        items=[
            DistributableItem(
                distribution_ids=[],
                project_id=project_id,
                report_definition_id=report_definition.id,
                node_id=UUID("4283fefc-63f0-cd0e-873a-0000c6d07ef7"),
                formula_id=UUID("b77e90d3-593a-d699-fc1f-7cd5bb2e35cb"),
                supplied_item=SuppliedItem(
                    datasheet_id=project_details.datasheet_id,
                    element_def_id=UUID("f0f19c55-7067-cbbe-80c4-6d1fb6dfbdb0"),
                    child_reference_id=zero_uuid(),
                    organization_id=organization_id,
                ),
                summary=report.stages[0].summary,
                columns=[
                    ComputedValue(label="stage", value=1, unit=None),
                    ComputedValue(label="quantity", value=2, unit=None),
                    ComputedValue(label="product_name", value=3, unit=None),
                ],
                obsolete=False,
                creation_date_utc=static_clock.utcnow(),
            ),
            DistributableItem(
                distribution_ids=[],
                project_id=project_id,
                report_definition_id=report_definition.id,
                node_id=UUID("309cad68-386d-070c-415e-d7e70cad1946"),
                formula_id=UUID("1922995d-8401-6e51-c6b3-6d6f3c9f0ac9"),
                supplied_item=SuppliedItem(
                    datasheet_id=project_details.datasheet_id,
                    element_def_id=UUID("056a4ad6-83cb-f721-2455-68a8baa397f4"),
                    child_reference_id=zero_uuid(),
                    organization_id=organization_id,
                ),
                summary=report.stages[0].summary,
                columns={
                    ComputedValue(label="stage", value=4, unit=None),
                    ComputedValue(label="quantity", value=5, unit=None),
                    ComputedValue(label="product_name", value=6, unit=None),
                },
                obsolete=False,
                creation_date_utc=static_clock.utcnow(),
            ),
        ],
        obsolete_distribution_ids=[],
    )


def test_update_populated_distributable_from_report(static_clock):
    project_id = uuid4()
    database_context = StrictInterfaceSetup(DatabaseContext)
    report_distributor = ReportDistributor(static_clock, database_context.object)
    report = ReportFactory(
        stages=[
            ReportStageFactory(
                rows=[
                    ReportRowFactory(
                        columns=[
                            ComputedValueFactory(value=1),
                            ComputedValueFactory(value=2),
                            ComputedValueFactory(value=3),
                        ]
                    ),
                    ReportRowFactory(
                        columns=[
                            ComputedValueFactory(value=4),
                            ComputedValueFactory(value=5),
                            ComputedValueFactory(value=6),
                        ]
                    ),
                ]
            )
        ]
    )
    report_definition = ReportDefinitionFactory(distributable=True)
    empty_distributable = []

    new_distributable = report_distributor.update_from_report(
        empty_distributable, report, report_definition
    )

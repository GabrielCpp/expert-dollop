from uuid import uuid4
from expert_dollup.core.units import ReportDistributor
from expert_dollup.core.domains import *
from ....fixtures import *


def test_update_with_report(static_clock):
    project_id = uuid4()
    report_distributor = ReportDistributor(static_clock)
    report = ReportFactory()
    report_definition = ReportDefinitionFactory(distributable=True)
    empty_distributable = Distributable(project_id, report_definition.id, [], [])

    report_distributor.update_from_report(
        empty_distributable, report, report_definition
    )

    print(empty_distributable)
    assert False

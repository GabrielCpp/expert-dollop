from expert_dollup.core.units import ReportDistributor
from expert_dollup.core.domains import *
from ..fixtures import *


def test_update_with_report(static_clock):
    report_distributor = ReportDistributor(static_clock)
    report
    report_definition
    empty_distributable = Distributable(
        project_id, report_definition_id, groups, distributions
    )

    report_distributor.update_from_report(
        empty_distributable, report, report_definition
    )

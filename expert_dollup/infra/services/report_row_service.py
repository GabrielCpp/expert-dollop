from expert_dollup.infra.expert_dollup_db import ReportRowDao
from expert_dollup.core.domains import ReportRow
from expert_dollup.shared.database_services import CollectionServiceProxy


class ReportRowService(CollectionServiceProxy[ReportRow]):
    class Meta:
        dao = ReportRowDao
        domain = ReportRow
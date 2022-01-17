from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.core.domains import DatasheetElement
from expert_dollup.infra.expert_dollup_db import DatasheetElementDao
from expert_dollup.core.domains import DatasheetElement


class DatasheetElementService(CollectionServiceProxy[DatasheetElement]):
    class Meta:
        dao = DatasheetElementDao
        domain = DatasheetElement

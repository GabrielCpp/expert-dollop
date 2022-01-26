from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import DatasheetDao
from expert_dollup.core.domains import Datasheet


class DatasheetService(CollectionServiceProxy[Datasheet]):
    class Meta:
        dao = DatasheetDao
        domain = Datasheet

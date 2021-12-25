from expert_dollup.core.domains import MeasureUnit
from expert_dollup.infra.expert_dollup_db import MeasureUnitDao
from expert_dollup.shared.database_services import CollectionServiceProxy


class MeasureUnitService(CollectionServiceProxy[MeasureUnit]):
    class Meta:
        dao = MeasureUnitDao
        domain = MeasureUnit
from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import DatasheetDefinitionElementDao
from expert_dollup.core.domains import DatasheetDefinitionElement


class DatasheetDefinitionElementService(
    CollectionServiceProxy[DatasheetDefinitionElement]
):
    class Meta:
        dao = DatasheetDefinitionElementDao
        domain = DatasheetDefinitionElement

from uuid import UUID
from typing import List
from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import ProjectFormulaInstanceDao
from expert_dollup.core.domains import FormulaInstance, FormulaInstanceFilter


class FormulaInstanceService(CollectionServiceProxy[FormulaInstance]):
    class Meta:
        dao = ProjectFormulaInstanceDao
        domain = FormulaInstance

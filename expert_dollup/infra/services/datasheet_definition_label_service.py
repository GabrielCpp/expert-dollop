from expert_dollup.shared.database_services import CollectionServiceProxy
from expert_dollup.infra.expert_dollup_db import LabelDao
from expert_dollup.core.domains import Label


class LabelService(CollectionServiceProxy[Label]):
    class Meta:
        dao = LabelDao
        domain = Label

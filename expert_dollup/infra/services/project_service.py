from expert_dollup.infra.expert_dollup_db import ProjectDao
from expert_dollup.core.domains import ProjectDetails
from expert_dollup.shared.database_services import CollectionServiceProxy


class ProjectService(CollectionServiceProxy[ProjectDetails]):
    class Meta:
        dao = ProjectDao
        domain = ProjectDetails

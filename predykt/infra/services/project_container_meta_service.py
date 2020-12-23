from predykt.infra.predykt_db import PredyktDatabase, project_container_meta_table, ProjectContainerMetaDao
from predykt.core.domains import ProjectContainerMeta
from predykt.shared.database_services import BaseCompositeCrudTableService


class ProjectContainerMetaService(BaseCompositeCrudTableService[ProjectContainerMeta]):
    class Meta:
        table = project_container_meta_table
        dao = ProjectContainerMetaDao
        domain = ProjectContainerMeta
        seach_filters = {}

from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_container_meta_table,
    ProjectContainerMetaDao,
)
from expert_dollup.core.domains import ProjectContainerMeta, ProjectContainerMetaFilter
from expert_dollup.shared.database_services import BaseCompositeCrudTableService


class ProjectContainerMetaService(BaseCompositeCrudTableService[ProjectContainerMeta]):
    class Meta:
        table = project_container_meta_table
        dao = ProjectContainerMetaDao
        domain = ProjectContainerMeta
        seach_filters = {}
        table_filter_type = ProjectContainerMetaFilter

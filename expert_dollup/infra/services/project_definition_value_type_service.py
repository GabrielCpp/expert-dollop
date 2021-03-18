from expert_dollup.infra.expert_dollup_db import (
    ExpertDollupDatabase,
    project_definition_value_type_table,
    ProjectDefinitionValueTypeDao,
)
from expert_dollup.core.domains import ProjectDefinitionValueType
from expert_dollup.shared.database_services import BaseCrudTableService


class ProjectDefinitionValueTypeService(
    BaseCrudTableService[ProjectDefinitionValueType]
):
    class Meta:
        table = project_definition_value_type_table
        dao = ProjectDefinitionValueTypeDao
        domain = ProjectDefinitionValueType
        table_filter_type = None

from expert_dollup.shared.database_services import (
    CollectionPaginator,
    FieldTokenEncoder,
)
from expert_dollup.core.domains import ProjectDefinitionNode


class ProjectDefinitionNodePaginator(CollectionPaginator[ProjectDefinitionNode]):
    class Meta:
        default_page_encoder = FieldTokenEncoder("name", str, str, "")
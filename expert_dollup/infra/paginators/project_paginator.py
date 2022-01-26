from expert_dollup.shared.database_services import (
    CollectionPaginator,
    FieldTokenEncoder,
)
from expert_dollup.core.domains import ProjectDetails


class ProjectPaginator(CollectionPaginator[ProjectDetails]):
    class Meta:
        default_page_encoder = FieldTokenEncoder("name", str, str, "")

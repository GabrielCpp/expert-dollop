from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class ProjectContainerMeta:
    project_id: UUID
    type_id: UUID
    state: dict


class ProjectContainerMetaFilter(QueryFilter):
    project_id: Optional[UUID]
    type_id: Optional[UUID]
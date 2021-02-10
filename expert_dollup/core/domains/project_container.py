from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class ProjectContainer:
    id: UUID
    project_id: UUID
    type_id: UUID
    path: List[UUID]
    value: dict

    @property
    def subpath(self):
        return [*self.path, self.id]


class ProjectContainerFilter(QueryFilter):
    id: Optional[UUID]
    project_id: Optional[UUID]
    type_id: Optional[UUID]
    path: Optional[List[UUID]]
    value: Optional[dict]

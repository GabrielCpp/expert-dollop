from expert_dollup.shared.starlette_injection import CamelModel
from uuid import UUID
from typing import List


class UserDto(CamelModel):
    oauth_id: str
    id: UUID
    email: str
    permissions: List[str]
    organization_id: UUID

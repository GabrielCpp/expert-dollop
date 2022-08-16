from uuid import UUID
from expert_dollup.shared.starlette_injection import CamelModel


class RessourceBatchImportDto(CamelModel):
    user_id: UUID

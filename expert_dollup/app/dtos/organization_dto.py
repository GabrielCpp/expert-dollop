from uuid import UUID
from expert_dollup.shared.starlette_injection import CamelModel


class NewSingleUserOrganizationDto(CamelModel):
    organization_name: str
    email: str

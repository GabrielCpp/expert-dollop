from uuid import UUID
from expert_dollup.shared.starlette_injection import CamelModel


class NewSingleUserOrganisationDto(CamelModel):
    organisation_name: str
    email: str
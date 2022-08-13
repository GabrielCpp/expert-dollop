from uuid import UUID
from expert_dollup.shared.starlette_injection import CamelModel


class OrganizationLimitsDto(CamelModel):
    active_project_count: int
    active_project_overall_collection_count: int
    active_datasheet_count: int
    active_datasheet_custom_element_count: int


class OrganizationDto(CamelModel):
    id: UUID
    name: str
    email: str
    limits: OrganizationLimitsDto


class NewSingleUserOrganizationDto(CamelModel):
    organization_name: str
    email: str

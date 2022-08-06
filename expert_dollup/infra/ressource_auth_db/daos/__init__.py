from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID
from expert_dollup.shared.database_services import DbConnection


class RessourceAuthDatabase(DbConnection):
    pass


class RessourceDao(BaseModel):
    class Meta:
        pk = ("id", "organization_id")

    class Config:
        title = "ressource"

    id: UUID
    kind: str = Field(max_length=64)
    organization_id: UUID
    permissions: List[str]
    name: List[str]
    creation_date_utc: datetime
    date_ordering: str


class UserDao(BaseModel):
    class Meta:
        pk = "oauth_id"

    class Config:
        title = "user"

    oauth_id: str
    id: UUID
    email: str
    permissions: List[str]
    organization_id: UUID


class OrganizationLimitsDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "organization_limits"

    active_project_count: int
    active_project_overall_collection_count: int
    active_datasheet_count: int
    active_datasheet_custom_element_count: int


class OrganizationDao(BaseModel):
    class Meta:
        pk = "id"

    class Config:
        title = "organization"

    id: UUID
    name: str
    limits: OrganizationLimitsDao

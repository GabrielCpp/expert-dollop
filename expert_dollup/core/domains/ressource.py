from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class Ressource:
    id: UUID
    kind: str
    organization_id: UUID
    permissions: List[str]
    name: str
    creation_date_utc: datetime


@dataclass
class OrganizationLimits:
    active_project_count: int
    active_project_overall_collection_count: int
    active_datasheet_count: int
    active_datasheet_custom_element_count: int


@dataclass
class Organization:
    id: UUID
    name: str
    limits: OrganizationLimits


@dataclass
class User:
    oauth_id: str
    id: UUID
    email: str
    permissions: List[str]
    organization_id: UUID


@dataclass
class RessourceId:
    id: UUID
    organization_id: UUID


class RessourceFilter(QueryFilter):
    id: Optional[UUID]
    organization_id: Optional[UUID]


class UserFilter(QueryFilter):
    id: Optional[UUID]

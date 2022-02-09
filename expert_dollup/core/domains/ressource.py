from dataclasses import dataclass
from uuid import UUID
from typing import List, Optional
from datetime import datetime
from expert_dollup.shared.database_services import QueryFilter


@dataclass
class Ressource:
    id: UUID
    kind: str
    user_id: UUID
    permissions: List[str]
    name: str
    creation_date_utc: datetime


@dataclass
class User:
    oauth_id: str
    id: UUID
    email: str
    permissions: List[str]


@dataclass
class RessourceId:
    id: UUID
    user_id: UUID


class RessourceFilter(QueryFilter):
    id: Optional[UUID]
    user_id: Optional[UUID]


class UserFilter(QueryFilter):
    id: Optional[UUID]
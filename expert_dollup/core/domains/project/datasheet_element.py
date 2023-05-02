from uuid import UUID
from typing import Optional, Dict, List
from dataclasses import dataclass
from datetime import datetime
from expert_dollup.shared.database_services import (
    QueryFilter,
    queries,
    Pluck,
    PluckSubRessource,
)
from functools import lru_cache
from ..values_union import PrimitiveUnion, PrimitiveWithReferenceUnion


@dataclass
class Attribute:
    name: str
    value: PrimitiveWithReferenceUnion


@dataclass
class DatasheetElement:
    id: UUID
    datasheet_id: UUID
    aggregate_id: UUID
    ordinal: int
    attributes: List[Attribute]
    original_datasheet_id: UUID
    original_owner_organization_id: UUID
    creation_date_utc: datetime

    @property
    def key(self) -> str:
        return ".".join(
            [self.datasheet_id, self.aggregate_id, self.child_element_reference]
        )

    @property
    def report_dict(self) -> dict:
        return {
            **self.attributes,
            "aggregate_id": self.aggregate_id,
            "element_id": self.id,
            "original_datasheet_id": self.original_datasheet_id,
        }


@dataclass
class NewDatasheetElement:
    aggregate_id: UUID
    ordinal: int
    attributes: List[Attribute]


@dataclass
class DatasheetElementUpdate(NewDatasheetElement):
    id: UUID


class DatasheetElementFilter(QueryFilter):
    id: Optional[UUID]
    datasheet_id: Optional[UUID]
    aggregate_id: Optional[UUID]
    ordinal: Optional[int]
    original_datasheet_id: Optional[UUID]
    original_owner_organization_id: Optional[UUID]
    creation_date_utc: Optional[datetime]


@queries.register_child_of(Pluck)
@queries.register_child_of(PluckSubRessource)
class DatasheetElementPluckFilter(DatasheetElementFilter):
    aggregate_ids: List[UUID]
    ids: List[UUID]

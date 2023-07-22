from uuid import UUID
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from expert_dollup.shared.database_services import QueryFilter
from expert_dollup.shared.validation import *
from ..values_union import PrimitiveWithReferenceUnion
from .translation import FieldTranslation, Translation


@dataclass
class AggregateAttribute:
    name: str
    is_readonly: bool
    value: PrimitiveWithReferenceUnion


@dataclass
class Aggregate:
    id: UUID
    project_definition_id: UUID
    collection_id: UUID
    ordinal: int
    name: str
    is_extendable: bool
    attributes: Dict[str, AggregateAttribute] = field(default_factory=dict)

    def get_attribute(self, name: str):
        if name == "id":
            return self.id

        return self.attributes[name]

    @property
    def report_dict(self) -> dict:
        return {
            "id": self.id,
            "ordinal": self.ordinal,
            "name": self.name,
            "is_collection": self.is_extendable,
        }


@dataclass
class LocalizedAggregate:
    aggregate: Aggregate
    translations: List[Translation]

    async def validate(self) -> None:
        schema = ValidationSchema(
            root=Object(
                properties={
                    "aggregate": Object(
                        properties={
                            "id": Uuid(
                                constraints=[
                                    ConstraintReference(
                                        "identical-value", "aggregate_id"
                                    )
                                ]
                            ),
                            "project_definition_id": Uuid(
                                constraints=[
                                    ConstraintReference("project-definition-exists"),
                                    ConstraintReference(
                                        "identical-value", "project_definition_id"
                                    ),
                                ]
                            ),
                            "collection_id": Uuid(
                                constraints=[ConstraintReference("collection-exists")]
                            ),
                            "ordinal": Integer(minimum=0),
                            "name": String(
                                pattern=STRING_WITH_UNDERSCORE,
                                constraints=[
                                    ConstraintReference("unique", "aggregate-name")
                                ],
                            ),
                            "is_extendable": Boolean(),
                            "attributes": Object(
                                pattern_properties={
                                    STRING_WITH_UNDERSCORE: Object(
                                        {
                                            "name": String(
                                                pattern=STRING_WITH_UNDERSCORE,
                                                constraints=[
                                                    ConstraintReference(
                                                        "unique", "attribute-name"
                                                    )
                                                ],
                                            ),
                                            "is_readonly": Boolean(),
                                            "value": Anything(),
                                        }
                                    )
                                }
                            ),
                        }
                    ),
                    "translations": Array(
                        Object(
                            {
                                "ressource_id": Uuid(
                                    constraints=[
                                        ConstraintReference(
                                            "identical-value", "project_definition_id"
                                        )
                                    ]
                                ),
                                "locale": String(enum=["en-ca", "fr-ca"]),
                                "scope": Uuid(
                                    constraints=[
                                        ConstraintReference(
                                            "identical-value", "aggregate_id"
                                        )
                                    ]
                                ),
                                "name": String(pattern=STRING_WITH_UNDERSCORE),
                                "value": String(max_length=500),
                                "creation_date_utc": String(format="date-time"),
                            }
                        )
                    ),
                }
            )
        )
        await validate_object(schema, self)


@dataclass
class NewAggregate:
    ordinal: int
    name: str
    is_extendable: bool
    attributes: List[AggregateAttribute]
    translated: List[FieldTranslation]


class AggregateFilter(QueryFilter):
    id: Optional[UUID]
    project_definition_id: Optional[UUID]
    collection_id: Optional[UUID]
    ordinal: Optional[int]
    name: Optional[str]

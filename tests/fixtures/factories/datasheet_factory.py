from typing import Dict, List, Optional, Union, Type
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from .helpers import make_uuid
from expert_dollup.core.domains import *
from expert_dollup.infra.json_schema import (
    INT_JSON_SCHEMA,
    STRING_JSON_SCHEMA,
    BOOL_JSON_SCHEMA,
    NUMBER_JSON_SCHEMA,
)

DEFAULT_VALUE_MAPPING = {
    int: INT_JSON_SCHEMA,
    str: STRING_JSON_SCHEMA,
    bool: BOOL_JSON_SCHEMA,
    float: NUMBER_JSON_SCHEMA,
}

DEFAULT_VALUE_GENERATOR = {
    int: lambda x: x * 2,
    str: lambda x: f"value{x}",
    bool: lambda x: x % 2 == 0,
    float: lambda x: x + float(x) / 100,
}


@dataclass
class CustomDatasheetInstancePackage:
    datasheet_definition: DatasheetDefinition
    datasheet_definition_elements: List[DatasheetDefinitionElement]
    datasheet: Datasheet
    datasheet_elements: List[DatasheetElement]
    label_collections: List[LabelCollection]
    labels: List[Label]
    translations: List[Translation]


PropertyTypeUnion = Union[Type[int], Type[float], Type[str], Type[bool]]


class ElementSeed:
    def __init__(self, unit_id: str, is_collection: bool = False, tags: List[str] = []):
        self._name: Optional[str] = None
        self.unit_id = unit_id
        self.is_collection = is_collection
        self._tags_name = list(tags)

    def tags_name(self) -> List[str]:
        return self._tags_name

    def tags(self) -> UUID:
        return [make_uuid(name) for name in self.tags_name]

    @property
    def id(self):
        return make_uuid(self.name)

    @property
    def name(self) -> str:
        assert not self._name is None
        return self._name

    def seed_value(self, property_type: PropertyTypeUnion, index: int):
        return DEFAULT_VALUE_GENERATOR[property_type](index)

    def backfill(self, name):
        self._name = name


@dataclass
class LabelSeed:
    name: str
    properties: Dict[str, ValueUnion]
    aggregates: Dict[str, UUID]

    @property
    def id(self) -> UUID:
        return make_uuid(self.name)


class CollectionSeed:
    def __init__(
        self,
        label_count: int,
        properties: Dict[str, PropertyTypeUnion],
        aggregates: Dict[str, LabelAttributeSchemaUnion],
    ):
        self.label_count = label_count
        self._property_seeds = properties
        self.properties = {
            name: DEFAULT_VALUE_MAPPING[property_type]
            for name, property_type in properties.items()
        }
        self.aggregates = aggregates
        self.label_seeds: List[LabelSeed] = []
        self._name: Optional[str] = None

    @property
    def name(self) -> str:
        assert not self._name is None
        return self._name

    @property
    def id(self) -> UUID:
        return make_uuid(self._name)

    def backfill(self, name):
        self._name = name
        self.label_seeds = [
            LabelSeed(
                name=f"{name}_label_{index}",
                properties={
                    name: DEFAULT_VALUE_GENERATOR[property_type]
                    for name, property_type in self._property_seeds.items()
                },
                aggregates={},
            )
            for index in range(0, self.label_count)
        ]


@dataclass
class DatasheetSeed:
    properties: Dict[str, PropertyTypeUnion]
    element_seeds: Dict[str, ElementSeed]
    collection_seeds: Dict[str, CollectionSeed]

    def __post_init__(self):
        for name, element_seed in self.element_seeds.items():
            element_seed.backfill(name)

        for name, collection_seed in self.collection_seeds.items():
            collection_seed.backfill(name)


class DatasheetInstanceFactory:
    @staticmethod
    def build(
        datasheet_seed: DatasheetSeed, datasheet_name: str = "test"
    ) -> CustomDatasheetInstancePackage:
        datasheet_definition = DatasheetDefinition(
            id=make_uuid(f"{datasheet_name}-definition"),
            name=f"{datasheet_name}-definition",
            properties={
                name: dict(DEFAULT_VALUE_MAPPING[property_type])
                for name, property_type in datasheet_seed.properties.items()
            },
        )

        datasheet = Datasheet(
            id=make_uuid(datasheet_name),
            is_staged=False,
            datasheet_def_id=datasheet_definition.id,
            name=datasheet_name,
            from_datasheet_id=make_uuid(datasheet_name),
            creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000),
        )

        datasheet_definition_elements = [
            DatasheetDefinitionElement(
                id=element_seed.id,
                unit_id=element_seed.unit_id,
                is_collection=element_seed.is_collection,
                datasheet_def_id=datasheet_definition.id,
                order_index=index,
                name=element_seed.name,
                default_properties={
                    name: DatasheetDefinitionElementProperty(
                        is_readonly=False,
                        value=element_seed.seed_value(property_type, index),
                    )
                    for name, property_type in datasheet_seed.properties.items()
                },
                tags=element_seed.tags,
                creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000),
            )
            for index, element_seed in enumerate(datasheet_seed.element_seeds.values())
        ]

        datasheet_elements = [
            DatasheetElement(
                datasheet_id=datasheet.id,
                element_def_id=element_seed.id,
                child_element_reference=zero_uuid(),
                properties={
                    name: element_seed.seed_value(property_type, index)
                    for name, property_type in datasheet_seed.properties.items()
                },
                original_datasheet_id=datasheet.id,
                creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000),
            )
            for index, element_seed in enumerate(datasheet_seed.element_seeds.values())
        ]

        label_collections = [
            LabelCollection(
                id=collection_seed.id,
                datasheet_definition_id=datasheet_definition.id,
                name=collection_seed.name,
                attributes_schema={
                    **collection_seed.properties,
                    **collection_seed.aggregates,
                },
            )
            for collection_seed in datasheet_seed.collection_seeds.values()
        ]

        labels: List[Label] = []

        for collection_seed in datasheet_seed.collection_seeds.values():
            for index, label_seed in enumerate(collection_seed.label_seeds):
                labels.append(
                    Label(
                        id=label_seed.id,
                        label_collection_id=collection_seed.id,
                        order_index=index,
                        attributes={**label_seed.properties, **label_seed.aggregates},
                    )
                )

        return CustomDatasheetInstancePackage(
            datasheet_definition=datasheet_definition,
            datasheet=datasheet,
            datasheet_definition_elements=datasheet_definition_elements,
            datasheet_elements=datasheet_elements,
            label_collections=label_collections,
            labels=labels,
            translations=[],
        )

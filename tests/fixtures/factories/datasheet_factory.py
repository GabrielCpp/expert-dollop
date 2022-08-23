from decimal import Decimal
from typing import Dict, List, Optional, Union, Type, Protocol
from typing_extensions import TypeAlias
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from itertools import islice
from uuid import UUID
from .helpers import make_uuid
from expert_dollup.core.domains import *
from expert_dollup.core.units.node_value_validation import (
    INT_JSON_SCHEMA,
    STRING_JSON_SCHEMA,
    BOOL_JSON_SCHEMA,
    DECIMAL_JSON_SCHEMA,
)

DEFAULT_VALUE_MAPPING = {
    int: INT_JSON_SCHEMA,
    str: STRING_JSON_SCHEMA,
    bool: BOOL_JSON_SCHEMA,
    Decimal: DECIMAL_JSON_SCHEMA,
}

DEFAULT_VALUE_GENERATOR = {
    int: lambda x: x * 2,
    str: lambda x: f"value{x}",
    bool: lambda x: x % 2 == 0,
    Decimal: lambda x: x + Decimal(x) / 100,
}


class FormulaLike(Protocol):
    id: UUID


@dataclass
class CustomDatasheetInstancePackage:
    project_definition: ProjectDefinition
    datasheet_definition_elements: List[DatasheetDefinitionElement]
    datasheet: Datasheet
    datasheet_elements: List[DatasheetElement]
    label_collections: List[LabelCollection]
    labels: List[Label]
    translations: List[Translation]


PropertyTypeUnion: TypeAlias = Union[Type[int], Type[Decimal], Type[str], Type[bool]]


class ElementSeed:
    def __init__(
        self,
        unit_id: str,
        is_collection: bool = False,
        tags: Optional[List[str]] = None,
    ):
        self.unit_id = unit_id
        self.is_collection = is_collection
        self._tags_name = tags or []
        self._name: Optional[str] = None

    @property
    def tags_name(self) -> List[str]:
        return self._tags_name

    @property
    def tags(self) -> UUID:
        return [make_uuid(name) for name in self.tags_name]

    @property
    def id(self):
        return make_uuid(self.name)

    def make_element_id(self, index: int) -> UUID:
        return make_uuid(f"{self.name}-{index}")

    @property
    def name(self) -> str:
        assert not self._name is None
        return self._name

    def seed_value(self, property_type: PropertyTypeUnion, index: int):
        return DEFAULT_VALUE_GENERATOR[property_type](index)

    def backfill(self, name: str, datasheet_seed: "DatasheetSeed"):
        self._name = name
        self.translations = [
            Translation(
                id=make_uuid(f"t_{locale.lower()}_element_{name}"),
                ressource_id=datasheet_seed.id,
                locale=locale,
                scope=self.id,
                name=self.name,
                value=f"t_{locale.lower()}_element_{name}",
                creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000),
            )
            for locale in datasheet_seed.locales
        ]


@dataclass
class LabelSeed:
    name: str
    attributes: Dict[str, LabelAttributeUnion]

    @property
    def id(self) -> UUID:
        return make_uuid(self.name)


class CollectionSeed:
    def __init__(
        self,
        label_count: int,
        schemas: Optional[Dict[str, PropertyTypeUnion]] = None,
        translations: Optional[Dict[str, Dict[str, str]]] = None,
    ):
        self.label_count = label_count
        self._attributes_seed = schemas or {}
        self.translation_seed = {}
        self._name: Optional[str] = None
        self._translations = translations
        self.label_seeds: List[LabelSeed] = []

    @property
    def attributes_schema(self) -> Dict[str, LabelAttributeSchemaUnion]:
        return {
            name: StaticProperty(DEFAULT_VALUE_MAPPING[property_type])
            if property_type in DEFAULT_VALUE_MAPPING
            else property_type
            for name, property_type in self._attributes_seed.items()
        }

    @property
    def name(self) -> str:
        assert not self._name is None
        return self._name

    @property
    def id(self) -> UUID:
        return make_uuid(self._name)

    @property
    def translations(self) -> List[Translation]:
        assert not self._translations is None
        translations: List[Translation] = []

        for locale, translations_for_locale in self._translations.items():
            for name, label in translations_for_locale.items():
                translations.append(
                    Translation(
                        id=make_uuid(label),
                        ressource_id=self.id,
                        locale=locale,
                        scope=make_uuid(name),
                        name=name,
                        value=label,
                        creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000),
                    )
                )

        return translations

    def backfill(self, name: str, datasheet_seed: "DatasheetSeed"):
        self._name = name
        self.label_seeds = [
            LabelSeed(
                name=f"{name}_label_{index}",
                attributes={
                    name: DEFAULT_VALUE_GENERATOR[property_type](index)
                    for name, property_type in self._attributes_seed.items()
                    if property_type in DEFAULT_VALUE_GENERATOR
                },
            )
            for index in range(0, self.label_count)
        ]

        if self._translations is None:
            self._translations = defaultdict(dict)

            for locale in datasheet_seed.locales:
                for index in range(0, self.label_count):
                    self._translations[locale][
                        f"{name}_label_{index}"
                    ] = f"t_{locale.lower()}_{name}_label_{index}"

    def backfill_label(self, datasheet_seed: "DatasheetSeed"):
        for index, label_seed in enumerate(self.label_seeds):
            for name, property_type in self._attributes_seed.items():
                if not property_type in DEFAULT_VALUE_GENERATOR:
                    assert isinstance(
                        property_type,
                        (CollectionAggregate, DatasheetAggregate, FormulaAggregate),
                    )

                    if isinstance(property_type, CollectionAggregate):
                        label_seeds = datasheet_seed.collection_seeds[
                            property_type.from_collection
                        ].label_seeds
                        assert len(label_seeds) > 1
                        label_seed.attributes[name] = label_seeds[
                            index % len(label_seeds)
                        ].id

                    if isinstance(property_type, DatasheetAggregate):
                        assert len(datasheet_seed.element_seeds) > 1
                        label_seed.attributes[name] = next(
                            islice(
                                datasheet_seed.element_seeds.values(),
                                index % len(datasheet_seed.element_seeds),
                                None,
                            )
                        ).id

                    if isinstance(property_type, FormulaAggregate):
                        assert not datasheet_seed.formulas is None
                        assert len(datasheet_seed.formulas) > 1
                        label_seed.attributes[name] = datasheet_seed.formulas[
                            index % len(datasheet_seed.formulas)
                        ].id


@dataclass
class DatasheetSeed:
    properties: Dict[str, PropertyTypeUnion]
    element_seeds: Dict[str, ElementSeed]
    collection_seeds: Dict[str, CollectionSeed]
    locales: List[str] = field(default_factory=lambda: ["fr-CA", "en-US"])
    name: str = "test"
    formulas: Optional[List[FormulaLike]] = None

    @property
    def id(self) -> str:
        return make_uuid(self.name)

    def __post_init__(self):
        for name, element_seed in self.element_seeds.items():
            element_seed.backfill(name, self)

        for name, collection_seed in self.collection_seeds.items():
            collection_seed.backfill(name, self)

        for collection_seed in self.collection_seeds.values():
            collection_seed.backfill_label(self)


class DatasheetInstanceFactory:
    @staticmethod
    def build(
        datasheet_seed: DatasheetSeed, project_definition: ProjectDefinition
    ) -> CustomDatasheetInstancePackage:
        original_owner_organization_id = make_uuid(
            f"{project_definition.name}-default-datasheet-owner"
        )
        project_definition.properties = {
            name: dict(DEFAULT_VALUE_MAPPING[property_type])
            for name, property_type in datasheet_seed.properties.items()
        }

        datasheet = Datasheet(
            id=make_uuid(f"{project_definition.name}-default-datasheet"),
            is_staged=False,
            project_definition_id=project_definition.id,
            name=datasheet_seed.name,
            from_datasheet_id=make_uuid(datasheet_seed.name),
            creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000),
        )

        datasheet_definition_elements = [
            DatasheetDefinitionElement(
                id=element_seed.id,
                unit_id=element_seed.unit_id,
                is_collection=element_seed.is_collection,
                project_definition_id=project_definition.id,
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
                child_element_reference=element_seed.make_element_id(0),
                ordinal=0,
                properties={
                    name: element_seed.seed_value(property_type, index)
                    for name, property_type in datasheet_seed.properties.items()
                },
                original_datasheet_id=datasheet.id,
                original_owner_organization_id=original_owner_organization_id,
                creation_date_utc=datetime(2011, 11, 4, 0, 5, 23, 283000),
            )
            for index, element_seed in enumerate(datasheet_seed.element_seeds.values())
        ]

        label_collections = [
            LabelCollection(
                id=collection_seed.id,
                project_definition_id=project_definition.id,
                name=collection_seed.name,
                attributes_schema=collection_seed.attributes_schema,
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
                        name=label_seed.name,
                        attributes=label_seed.attributes,
                    )
                )

        translations: List[Translation] = []

        for element_seed in datasheet_seed.element_seeds.values():
            translations.extend(element_seed.translations)

        for collection_seed in datasheet_seed.collection_seeds.values():
            translations.extend(collection_seed.translations)

        return CustomDatasheetInstancePackage(
            project_definition=project_definition,
            datasheet=datasheet,
            datasheet_definition_elements=datasheet_definition_elements,
            datasheet_elements=datasheet_elements,
            label_collections=label_collections,
            labels=labels,
            translations=translations,
        )

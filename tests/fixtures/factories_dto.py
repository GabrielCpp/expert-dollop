import factory
from uuid import uuid4, UUID
from datetime import datetime, timezone
from expert_dollup.app.dtos import *


class ProjectDefinitionDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionDto

    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Gab{n}")
    datasheet_def_id = factory.LazyFunction(uuid4)
    default_datasheet_id = factory.LazyFunction(uuid4)


class ProjectDefinitionNodeDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionNodeDto

    id = factory.LazyFunction(uuid4)
    project_def_id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"Container{n}")
    is_collection = False
    instanciate_by_default = True
    order_index = factory.Sequence(lambda n: n)
    config = factory.LazyAttribute(
        lambda o: NodeConfigDto(
            field_details=IntFieldConfigDto(unit="Kg"),
            value_validator={"type": "integer", "minimum": 0, "maximum": 100000},
            triggers=[],
            translations=TranslationConfigDto(
                help_text_name=f"{o.name}_help_text", label=o.name
            ),
            meta=NodeMetaConfigDto(is_visible=True),
        )
    )
    default_value = IntFieldValueDto(integer=0)
    path = []


class TranslationDtoFactory(factory.Factory):
    class Meta:
        model = TranslationDto

    id = factory.LazyFunction(uuid4)
    ressource_id = factory.LazyFunction(uuid4)
    scope = factory.LazyFunction(uuid4)
    locale = "fr"
    name = factory.Sequence(lambda n: f"hello{n}")
    value = factory.Sequence(lambda n: f"translation{n}")
    creation_date_utc = factory.Sequence(lambda n: datetime.now(timezone.utc))


class TranslationInputDtoFactory(factory.Factory):
    class Meta:
        model = TranslationInputDto

    id = factory.LazyFunction(uuid4)
    ressource_id = factory.LazyFunction(uuid4)
    scope = factory.LazyFunction(uuid4)
    locale = "fr"
    name = factory.Sequence(lambda n: f"hello{n}")
    value = factory.Sequence(lambda n: f"translation{n}")


class ProjectDetailsDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDetailsDto

    id: UUID = factory.LazyFunction(uuid4)
    name: str = factory.Sequence(lambda n: f"project{n}")
    is_staged: bool = False
    project_def_id: UUID = factory.LazyFunction(uuid4)
    datasheet_id: UUID = factory.LazyFunction(uuid4)


class FormulaDtoFactory(factory.Factory):
    class Meta:
        model = FormulaDto

    id = factory.LazyFunction(uuid4)
    project_def_id = factory.LazyFunction(uuid4)
    attached_to_type_id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"formula{n}")
    expression = "a+b*c/2"


class DatasheetDefinitionDtoFactory(factory.Factory):
    class Meta:
        model = DatasheetDefinitionDto

    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"datasheet_definition{n}")
    properties = {
        "conversion_factor": ElementPropertySchemaDto(
            value_validator={"type": "number"}
        ),
        "lost": ElementPropertySchemaDto(value_validator={"type": "number"}),
    }


class DatasheetDefinitionElementDtoFactory(factory.Factory):
    class Meta:
        model = DatasheetDefinitionElementDto

    id = factory.LazyFunction(uuid4)
    unit_id = "inch"
    is_collection = False
    datasheet_def_id = factory.LazyFunction(uuid4)
    order_index = factory.Sequence(lambda n: n)
    tags = factory.LazyFunction(lambda: [])
    name = factory.Sequence(lambda n: f"field_name{n}")
    default_properties = {
        "conversion_factor": DatasheetDefinitionElementPropertyDto(
            is_readonly=True, value=2
        ),
        "lost": DatasheetDefinitionElementPropertyDto(is_readonly=True, value=2),
    }


class LabelCollectionDtoFactory(factory.Factory):
    class Meta:
        model = LabelCollectionDto

    id = factory.LazyFunction(uuid4)
    datasheet_definition_id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"label_collection_{n}")


class LabelDtoFactory(factory.Factory):
    class Meta:
        model = LabelDto

    id = factory.LazyFunction(uuid4)
    label_collection_id = factory.LazyFunction(uuid4)
    order_index = factory.Sequence(lambda n: n)


class DatasheetDtoFactory(factory.Factory):
    class Meta:
        model = NewDatasheetDto

    id = factory.LazyFunction(uuid4)
    name = factory.Sequence(lambda n: f"datasheet{n}")
    is_staged = False
    datasheet_def_id = factory.LazyFunction(uuid4)
    from_datasheet_id = factory.SelfAttribute("id")

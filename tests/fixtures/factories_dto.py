import factory
from datetime import timezone
from expert_dollup.app.dtos import *


class ProjectDefinitionDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionDto

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"Gab{n}")
    project_definition_id = factory.Faker("pyuuid4")
    default_datasheet_id = factory.Faker("pyuuid4")
    properties = {
        "conversion_factor": ElementPropertySchemaDto(
            value_validator={"type": "number"}
        ),
        "lost": ElementPropertySchemaDto(value_validator={"type": "number"}),
    }
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class IntFieldConfigDtoFactory(factory.Factory):
    class Meta:
        model = IntFieldConfigDto

    unit = "kg"
    integer = factory.Faker("pyint", min_value=0, max_value=1000)


class ProjectDefinitionNodeDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionNodeDto

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"Container{n}")
    is_collection = False
    instanciate_by_default = True
    order_index = factory.Sequence(lambda n: n)
    triggers = factory.List([])
    field_details = IntFieldConfigDtoFactory()
    meta = NodeMetaConfigDto(is_visible=True)
    translations = factory.LazyAttribute(
        lambda o: TranslationConfigDto(
            help_text_name=f"{o.name}_help_text", label=o.name
        )
    )
    validator = factory.LazyAttribute(
        lambda o: {"type": "integer", "minimum": 0, "maximum": 100000}
    )
    path = factory.List([])
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class TranslationDtoFactory(factory.Factory):
    class Meta:
        model = TranslationDto

    id = factory.Faker("pyuuid4")
    ressource_id = factory.Faker("pyuuid4")
    scope = factory.Faker("pyuuid4")
    locale = "fr-CA"
    name = factory.Sequence(lambda n: f"hello{n}")
    value = factory.Sequence(lambda n: f"translation{n}")
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class TranslationInputDtoFactory(factory.Factory):
    class Meta:
        model = TranslationInputDto

    id = factory.Faker("pyuuid4")
    ressource_id = factory.Faker("pyuuid4")
    scope = factory.Faker("pyuuid4")
    locale = "fr-CA"
    name = factory.Sequence(lambda n: f"hello{n}")
    value = factory.Sequence(lambda n: f"translation{n}")


class ProjectDetailsDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDetailsDto

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"project{n}")
    is_staged = False
    project_definition_id = factory.Faker("pyuuid4")
    datasheet_id = factory.Faker("pyuuid4")
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class NewProjectDetailsDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDetailsInputDto

    name = factory.Sequence(lambda n: f"project{n}")
    is_staged = False
    project_definition_id = factory.Faker("pyuuid4")
    datasheet_id = factory.Faker("pyuuid4")


class FormulaExpressionDtoFactory(factory.Factory):
    class Meta:
        model = FormulaExpressionDto

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
    attached_to_type_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"formula{n}")
    expression = "a+b*c/2"
    path = factory.LazyAttribute(lambda f: [f.attached_to_type_id])
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class DatasheetDefinitionElementDtoFactory(factory.Factory):
    class Meta:
        model = DatasheetDefinitionElementDto

    id = factory.Faker("pyuuid4")
    unit_id = "inch"
    is_collection = False
    project_definition_id = factory.Faker("pyuuid4")
    order_index = factory.Sequence(lambda n: n)
    tags = factory.LazyFunction(lambda: [])
    name = factory.Sequence(lambda n: f"field_name{n}")
    default_properties = factory.Dict(
        {
            "conversion_factor": DatasheetDefinitionElementPropertyDto(
                is_readonly=True, value=IntFieldValueDto(integer=2)
            ),
            "lost": DatasheetDefinitionElementPropertyDto(
                is_readonly=True, value=IntFieldValueDto(integer=2)
            ),
        }
    )
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class LabelCollectionDtoFactory(factory.Factory):
    class Meta:
        model = LabelCollectionDto

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"label_collection_{n}")
    attributes_schema = factory.Dict({})


class LabelDtoFactory(factory.Factory):
    class Meta:
        model = LabelDto

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"label_{n}")
    label_collection_id = factory.Faker("pyuuid4")
    order_index = factory.Sequence(lambda n: n)
    attributes = factory.Dict({})


class DatasheetDtoFactory(factory.Factory):
    class Meta:
        model = NewDatasheetDto

    name = factory.Sequence(lambda n: f"datasheet{n}")
    is_staged = False
    project_definition_id = factory.Faker("pyuuid4")
    from_datasheet_id = None

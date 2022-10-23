import factory
from datetime import timezone
from expert_dollup.app.dtos import *


class NewDefinitionDtoFactory(factory.Factory):
    class Meta:
        model = NewDefinitionDto

    name = factory.Sequence(lambda n: f"Gab{n}")


class ProjectDefinitionDtoFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionDto

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"Gab{n}")
    project_definition_id = factory.Faker("pyuuid4")
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
    ordinal = factory.Sequence(lambda n: n)
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


class NewAggregateCollectionDtoFactory(factory.Factory):
    class Meta:
        model = NewAggregateCollectionDto

    name = factory.Sequence(lambda n: f"new_aggregate_collection_{n}")
    is_abstract = False
    attributes_schema = factory.List([])


class AggregateCollectionDtoFactory(factory.Factory):
    class Meta:
        model = AggregateCollectionDto

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"aggregate_collection_{n}")
    is_abstract = False
    attributes_schema = factory.List([])


class NewAggregateDtoFactory(factory.Factory):
    class Meta:
        model = NewAggregateDto

    ordinal = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"label_{n}")
    is_extendable = False
    attributes = factory.List([])


class AggregateDtoFactory(factory.Factory):
    class Meta:
        model = AggregateDto

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"label_{n}")
    is_extendable = False
    ordinal = factory.Sequence(lambda n: n)
    attributes = factory.List([])


class NewDatasheetDtoFactory(factory.Factory):
    class Meta:
        model = NewDatasheetDto

    name = factory.Sequence(lambda n: f"datasheet{n}")
    project_definition_id = factory.Faker("pyuuid4")
    abstract_collection_id = factory.Faker("pyuuid4")

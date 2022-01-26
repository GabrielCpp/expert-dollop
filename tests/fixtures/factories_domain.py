import factory
from expert_dollup.core.domains import *
from datetime import timezone


class ProjectDefinitionFactory(factory.Factory):
    class Meta:
        model = ProjectDefinition

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"project_definition_{n}")
    default_datasheet_id = factory.Faker("pyuuid4")
    datasheet_def_id = factory.Faker("pyuuid4")
    creation_date_utc = factory.Faker("date_time", tzinfo=timezone.utc)


class ProjectDefinitionNodeFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionNode

    id = factory.Faker("pyuuid4")
    project_def_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"node{n}")
    is_collection = False
    instanciate_by_default = True
    order_index = factory.Sequence(lambda n: n)
    config = factory.LazyAttribute(
        lambda o: NodeConfig(
            translations=TranslationConfig(
                help_text_name=f"{o.name}_help_text", label=o.name
            )
        )
    )
    default_value = None
    path = factory.List([])
    creation_date_utc = factory.Faker("date_time", tzinfo=timezone.utc)


class ReportJoinFactory(factory.Factory):
    class Meta:
        model = ReportJoin

    from_object_name = factory.Sequence(lambda n: f"from_object_{n}")
    from_property_name = factory.Sequence(lambda n: f"from_property_{n}")
    to_object_name = factory.Sequence(lambda n: f"to_object_name_{n}")
    to_property_name = factory.Sequence(lambda n: f"to_property_name_{n}")
    alias_name = factory.Sequence(lambda n: f"alias_name_{n}")
    is_inner_join = True


class AttributeBucketFactory(factory.Factory):
    class Meta:
        model = AttributeBucket

    bucket_name = "bucket"
    attribute_name = "attribute"


class ReportStructureFactory(factory.Factory):
    class Meta:
        model = ReportStructure

    datasheet_selection_alias = "datasheet_element"
    joins = factory.List([factory.SubFactory(ReportJoinFactory) for _ in range(3)])
    formula_attribute = factory.SubFactory(AttributeBucketFactory)
    datasheet_attribute = factory.SubFactory(AttributeBucketFactory)
    columns = factory.List([])
    group_by = factory.List([])
    order_by = factory.List([])


class ReportComputationFactory(factory.Factory):
    class Meta:
        model = ReportComputation

    name = factory.Sequence(lambda n: f"property_{n}")
    expression = factory.Sequence(lambda n: f"property_{n}*2+1")


class ReportDefinitionFactory(factory.Factory):
    class Meta:
        model = ReportDefinition

    id = factory.Faker("pyuuid4")
    project_def_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"report_name_{n}")
    structure = factory.SubFactory(ReportStructureFactory)


class DatasheetDefinitionFactory(factory.Factory):
    class Meta:
        model = DatasheetDefinition

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"datasheet_definition_{n}")
    properties = factory.Dict({})


class DatasheetDefinitionElementFactory(factory.Factory):
    class Meta:
        model = DatasheetDefinitionElement

    id = factory.Faker("pyuuid4")
    unit_id: str
    is_collection: bool
    datasheet_def_id = factory.Faker("pyuuid4")
    order_index: int
    name: str
    default_properties = factory.Dict({})
    tags = factory.List([factory.Faker("pyuuid4")])
    creation_date_utc = factory.Faker("date_time", tzinfo=timezone.utc)


class LabelFactory(factory.Factory):
    class Meta:
        model = Label

    id = factory.Faker("pyuuid4")
    label_collection_id = factory.Faker("pyuuid4")
    order_index = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"label_{n}")
    attributes = factory.Dict({})


class LabelCollectionFactory(factory.Factory):
    class Meta:
        model = LabelCollection

    id = factory.Faker("pyuuid4")
    datasheet_definition_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"label_collection_{n}")
    attributes_schema = factory.Dict({})


class TranslationFactory(factory.Factory):
    class Meta:
        model = Translation

    id = factory.Faker("pyuuid4")
    ressource_id = factory.Faker("pyuuid4")
    locale = "fr_CA"
    scope = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"translation_{n}")
    value = factory.Sequence(lambda n: f"translation_value_{n}")
    creation_date_utc = factory.Faker("date_time", tzinfo=timezone.utc)

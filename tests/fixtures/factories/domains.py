import factory
from factory import SubFactory, fuzzy
from expert_dollup.core.domains import *
from datetime import timezone
from decimal import Decimal


class ProjectDefinitionFactory(factory.Factory):
    class Meta:
        model = ProjectDefinition

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"project_definition_{n}")
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class ProjectDefinitionNodeFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionNode

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"node{n}")
    is_collection = False
    instanciate_by_default = True
    ordinal = factory.Sequence(lambda n: n)
    translations = factory.LazyAttribute(
        lambda o: TranslationConfig(help_text_name=f"{o.name}_help_text", label=o.name)
    )
    field_details = None
    path = factory.List([])
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


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


class ReportComputationFactory(factory.Factory):
    class Meta:
        model = ReportComputation

    name = factory.Sequence(lambda n: f"property_{n}")
    expression = factory.Sequence(lambda n: f"property_{n}*2+1")
    unit = "unit"
    is_visible = True


class StageSummaryFactory(factory.Factory):
    class Meta:
        model = StageSummary

    label = factory.SubFactory(
        AttributeBucketFactory,
        bucket_name="columns",
        attribute_name="stage",
    )

    summary = factory.SubFactory(
        ReportComputationFactory,
        name="total",
        expression="sum(row['columns']['cost'] for row in rows)",
    )


class ReportStructureFactory(factory.Factory):
    class Meta:
        model = ReportStructure

    datasheet_selection_alias = "abstractproduct"
    formula_attribute = factory.SubFactory(
        AttributeBucketFactory, bucket_name="substage", attribute_name="formula"
    )
    datasheet_attribute = factory.SubFactory(
        AttributeBucketFactory,
        bucket_name="substage",
        attribute_name="datasheet_element",
    )
    stage_summary = factory.SubFactory(StageSummaryFactory)
    joins_cache = factory.List([])
    columns = factory.List(
        [
            factory.SubFactory(
                ReportComputationFactory,
                name="stage",
                expression="row['stage']['name']",
            ),
            factory.SubFactory(
                ReportComputationFactory,
                name="quantity",
                expression="row['formula']['result']",
            ),
            factory.SubFactory(
                ReportComputationFactory,
                name="product_name",
                expression="row['datasheet_element']['name']",
            ),
            factory.SubFactory(
                ReportComputationFactory,
                name="cost_per_unit",
                expression="row['datasheet_element']['price']",
                unit="$",
            ),
            factory.SubFactory(
                ReportComputationFactory,
                name="cost",
                expression="row['columns']['quantity'] * row['columns']['cost_per_unit']",
                unit="$",
            ),
        ]
    )
    group_by = factory.List(
        [
            factory.SubFactory(
                AttributeBucketFactory,
                bucket_name="columns",
                attribute_name="stage",
            ),
            factory.SubFactory(
                AttributeBucketFactory,
                bucket_name="columns",
                attribute_name="product_name",
            ),
        ]
    )
    order_by = factory.List(
        [
            factory.SubFactory(
                AttributeBucketFactory,
                bucket_name="substage",
                attribute_name="ordinal",
            )
        ]
    )
    report_summary = factory.List(
        [
            factory.SubFactory(
                ReportComputationFactory,
                name="subtotal",
                expression="sum(stage.summary.value for stage in stages)",
                unit="$",
            ),
        ]
    )


class ReportDefinitionFactory(factory.Factory):
    class Meta:
        model = ReportDefinition

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
    from_aggregate_collection_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"report_name_{n}")
    structure = factory.SubFactory(ReportStructureFactory)
    distributable = False


class ComputedValueFactory(factory.Factory):
    class Meta:
        model = ComputedValue

    label = factory.Sequence(lambda n: f"computed_value_{n}")
    value = factory.Sequence(lambda n: n)
    unit = "$"


class ReportRowFactory(factory.Factory):
    class Meta:
        model = ReportRow

    node_id = factory.Faker("pyuuid4")
    formula_id = factory.Faker("pyuuid4")
    aggregate_id = factory.Faker("pyuuid4")
    element_id = factory.Faker("pyuuid4")
    columns = factory.List([SubFactory(ComputedValueFactory) for _ in range(3)])
    row = factory.Dict({})


class StageColumnFactory(factory.Factory):
    class Meta:
        model = StageColumn

    label = factory.Sequence(lambda n: f"computed_value_{n}")
    unit = "$"
    is_visible: bool = True


class ReportStageFactory(factory.Factory):
    class Meta:
        model = ReportStage

    summary = SubFactory(ComputedValueFactory)
    rows = factory.List([SubFactory(ReportRowFactory) for _ in range(3)])
    columns = factory.List([SubFactory(StageColumnFactory) for _ in range(3)])


class ReportKeyFactory(factory.Factory):
    class Meta:
        model = ReportKey

    project_id = factory.Faker("pyuuid4")
    report_definition_id = factory.Faker("pyuuid4")


class ReportFactory(factory.Factory):
    class Meta:
        model = Report

    name = factory.Sequence(lambda n: f"report_name_{n}")
    datasheet_id = factory.Faker("pyuuid4")
    stages = factory.List([SubFactory(ReportStageFactory) for _ in range(3)])
    summaries = factory.List([SubFactory(ComputedValueFactory) for _ in range(3)])
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class IntFieldConfigFactory(factory.Factory):
    class Meta:
        model = IntFieldConfig

    unit = None
    default_value = factory.Faker("pyint")


class DecimalFieldConfigFactory(factory.Factory):
    class Meta:
        model = DecimalFieldConfig

    unit = "inch"
    precision = 3
    default_value = factory.Faker("pydecimal")


class StringFieldConfigFactory(factory.Factory):
    class Meta:
        model = StringFieldConfig

    transforms = ["trim"]
    default_value = factory.Faker("word")


class BoolFieldConfigFactory(factory.Factory):
    class Meta:
        model = BoolFieldConfig

    default_value = factory.Faker("pybool")


class StaticChoiceOptionFactory(factory.Factory):
    class Meta:
        model = StaticChoiceOption

    id = factory.Faker("unique_name_id")
    label = factory.Faker("underscored_name")
    help_text = factory.Faker("underscored_name")


class StaticChoiceFieldConfigFactory(factory.Factory):
    class Meta:
        model = StaticChoiceFieldConfig

    options = factory.RelatedFactoryList(
        StaticChoiceOptionFactory, size=lambda: factory.fuzzy.FuzzyInteger(0, 3).fuzz()
    )
    default_value = factory.LazyAttribute(
        lambda o: o.options[factory.fuzzy.FuzzyInteger(0, len(o.options)).fuzz()].id
    )


class AggregateCollectionFactory(factory.Factory):
    class Meta:
        model = AggregateCollection

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"aggregate_collection_{n}")
    is_abstract = False
    attributes_schema = factory.Dict({})


class AggregateAttributeSchemaFactory(factory.Factory):
    class Meta:
        model = AggregateAttributeSchema

    name = factory.Sequence(lambda n: f"attribute_{n}")
    details = factory.SubFactory(IntFieldConfigFactory)


class AggregateFactory(factory.Factory):
    class Meta:
        model = Aggregate

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
    collection_id = factory.Faker("pyuuid4")
    ordinal = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"label_{n}")
    is_extendable = False
    attributes = factory.Dict({})


class AggregateAttributeFactory(factory.Factory):
    class Meta:
        model = AggregateAttribute

    name = factory.Faker("underscored_name")
    is_readonly = factory.Faker("pybool")
    value = fuzzy.FuzzyChoice(
        [
            fuzzy.FuzzyChoice([True, False]),
            fuzzy.FuzzyInteger(0),
            fuzzy.FuzzyDecimal(0),
        ],
        lambda x: x.fuzz(),
    )


class TranslationFactory(factory.Factory):
    class Meta:
        model = Translation

    id = factory.Faker("pyuuid4")
    ressource_id = factory.Faker("pyuuid4")
    locale = "fr-CA"
    scope = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"translation_{n}")
    value = factory.Sequence(lambda n: f"translation_value_{n}")
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class ProjectDetailsFactory(factory.Factory):
    class Meta:
        model = ProjectDetails

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"project{n}")
    is_staged = False
    project_definition_id = factory.Faker("pyuuid4")
    datasheet_id = factory.Faker("pyuuid4")
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class OrganizationLimitsFactory(factory.Factory):
    class Meta:
        model = OrganizationLimits

    active_project_count = 40
    active_project_overall_collection_count = 40
    active_datasheet_count = 40
    active_datasheet_custom_element_count = 40


class OrganizationFactory(factory.Factory):
    class Meta:
        model = Organization

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"Organization{n}")
    limits = factory.SubFactory(OrganizationLimitsFactory)


class UserFactory(factory.Factory):
    class Meta:
        model = User

    oauth_id = factory.Sequence(lambda n: f"user{n}")
    id = factory.Faker("pyuuid4")
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    permissions = factory.List([])
    organization_id = factory.Faker("pyuuid4")


class DatasheetFactory(factory.Factory):
    class Meta:
        model = Datasheet

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"name{n}")
    project_definition_id = factory.Faker("pyuuid4")
    abstract_collection_id = factory.Faker("pyuuid4")
    from_datasheet_id = factory.Faker("pyuuid4")
    attributes_schema = factory.Dict({})
    instances_schema = factory.Dict({})
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)

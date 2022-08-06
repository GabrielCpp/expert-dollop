import factory
from factory import SubFactory
from expert_dollup.core.domains import *
from datetime import timezone


class ProjectDefinitionFactory(factory.Factory):
    class Meta:
        model = ProjectDefinition

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"project_definition_{n}")
    default_datasheet_id = factory.Faker("pyuuid4")
    properties = factory.Dict({})
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class ProjectDefinitionNodeFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionNode

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
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
                attribute_name="order_index",
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
    element_def_id = factory.Faker("pyuuid4")
    child_reference_id = factory.Faker("pyuuid4")
    columns = factory.List([SubFactory(ComputedValueFactory) for _ in range(3)])
    row = factory.Dict({})


class ReportStageFactory(factory.Factory):
    class Meta:
        model = ReportStage

    summary = SubFactory(ComputedValueFactory)
    rows = factory.List([SubFactory(ReportRowFactory) for _ in range(3)])


class ReportKeyFactory(factory.Factory):
    class Meta:
        model = ReportKey

    project_id = factory.Faker("pyuuid4")
    report_definition_id = factory.Faker("pyuuid4")


class ReportFactory(factory.Factory):
    class Meta:
        model = Report

    datasheet_id = factory.Faker("pyuuid4")
    stages = factory.List([SubFactory(ReportStageFactory) for _ in range(3)])
    summaries = factory.List([SubFactory(ComputedValueFactory) for _ in range(3)])
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class DatasheetDefinitionElementFactory(factory.Factory):
    class Meta:
        model = DatasheetDefinitionElement

    id = factory.Faker("pyuuid4")
    unit_id: str
    is_collection: bool
    project_definition_id = factory.Faker("pyuuid4")
    order_index: int
    name: str
    default_properties = factory.Dict({})
    tags = factory.List([factory.Faker("pyuuid4")])
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


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
    project_definition_id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"label_collection_{n}")
    attributes_schema = factory.Dict({})


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

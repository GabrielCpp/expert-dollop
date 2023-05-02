import factory
from factory import SubFactory, fuzzy
from factory.declarations import BaseDeclaration
from datetime import timezone
from decimal import Decimal
from typing import *
from expert_dollup.core.domains import *
from expert_dollup.core.units.evaluator import ExpressionCompiler


class FlatAstAttribute(BaseDeclaration):
    """Specific BaseDeclaration computed using a lambda.

    Attributes:
        function (function): a function, expecting the current LazyStub and
            returning the computed value.
    """

    COMPILERS = {
        "simple": ExpressionCompiler.create_simple(),
        "complex": ExpressionCompiler.create_complex(),
    }

    def __init__(self, function, compiler_name):
        super().__init__()
        self.function = function
        self.compiler_name = compiler_name

    def evaluate(self, instance, step, extra):
        compiler = FlatAstAttribute.COMPILERS[self.compiler_name]
        return compiler.compile(self.function(instance)).dict()


class ProjectDefinitionFactory(factory.Factory):
    class Meta:
        model = ProjectDefinition

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"project_definition_{n}")
    revision = "0"
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


class CompiledReportKeyFactory(factory.Factory):
    class Meta:
        model = CompiledReportKey

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")


class SimpleExpressionFactory(factory.Factory):
    class Meta:
        model = Expression

    name: str
    flat_ast: Optional[dict] = FlatAstAttribute(lambda o: o.name, "simple")


class ComplexExpressionFactory(factory.Factory):
    class Meta:
        model = Expression

    name: str
    flat_ast: Optional[dict] = FlatAstAttribute(lambda o: o.name, "complex")


class ReportComputationFactory(factory.Factory):
    class Meta:
        model = ReportComputation

    name = factory.Sequence(lambda n: f"computation_{n}")
    expression = SimpleExpressionFactory(name="property*2+1")
    label = None
    unit = "unit"
    is_visible = True


class AttributeBucketFactory(factory.Factory):
    class Meta:
        model = AttributeBucket

    bucket_name = "bucket"
    attribute_name = "attribute"


class ReportJoinFactory(factory.Factory):
    class Meta:
        model = ReportJoin

    from_object = factory.SubFactory(
        AttributeBucketFactory,
        bucket_name="sources",
        attribute_name="id",
    )
    on_object = factory.SubFactory(
        AttributeBucketFactory,
        bucket_name="targets",
        attribute_name="id",
    )
    alias = factory.Sequence(lambda n: f"alias_name_{n}")


class SelectionFactory(factory.Factory):
    class Meta:
        model = Selection

    from_collection_id = factory.Faker("pyuuid4")
    from_alias = "abstractproduct"
    joins_cache = factory.List([])
    formula_attribute = factory.SubFactory(
        AttributeBucketFactory, bucket_name="substage", attribute_name="formula"
    )
    datasheet_attribute = factory.SubFactory(
        AttributeBucketFactory,
        bucket_name="substage",
        attribute_name="datasheet_element",
    )


class ReportStructureFactory(factory.Factory):
    class Meta:
        model = ReportStructure

    selection = factory.SubFactory(SelectionFactory)
    columns = factory.List(
        [
            factory.SubFactory(
                ReportComputationFactory,
                name="stage",
                expression=ComplexExpressionFactory(name="row['stage']['name']"),
            ),
            factory.SubFactory(
                ReportComputationFactory,
                name="quantity",
                expression=ComplexExpressionFactory(name="row['formula']['value']"),
            ),
            factory.SubFactory(
                ReportComputationFactory,
                name="product_name",
                expression=ComplexExpressionFactory(
                    name="row['datasheet_element']['name']"
                ),
            ),
            factory.SubFactory(
                ReportComputationFactory,
                name="cost_per_unit",
                expression=ComplexExpressionFactory(
                    name="row['datasheet_element']['price']"
                ),
                unit="$",
            ),
            factory.SubFactory(
                ReportComputationFactory,
                name="cost",
                expression=ComplexExpressionFactory(
                    name="row['columns']['quantity'] * row['columns']['cost_per_unit']"
                ),
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
    having = None
    order_by = factory.List(
        [
            factory.SubFactory(
                AttributeBucketFactory,
                bucket_name="substage",
                attribute_name="ordinal",
            )
        ]
    )
    stage_summary = factory.SubFactory(
        ReportComputationFactory,
        name="total",
        expression=ComplexExpressionFactory(
            name="sum(row['columns']['cost'] for row in rows)"
        ),
        label=factory.SubFactory(
            AttributeBucketFactory,
            bucket_name="columns",
            attribute_name="stage",
        ),
    )
    report_summary = factory.List(
        [
            factory.SubFactory(
                ReportComputationFactory,
                name="subtotal",
                expression=ComplexExpressionFactory(
                    name="sum(stage.summary.value for stage in stages)"
                ),
                unit="$",
            ),
        ]
    )


class ReportDefinitionFactory(factory.Factory):
    class Meta:
        model = ReportDefinition

    id = factory.Faker("pyuuid4")
    project_definition_id = factory.Faker("pyuuid4")
    name = factory.Faker("name")
    structure = factory.SubFactory(ReportStructureFactory)
    distributable = factory.Faker("random_element", elements=[True, False])


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


class FieldTranslationFactory(factory.Factory):
    class Meta:
        model = FieldTranslation

    locale = "fr-ca"
    name = factory.Sequence(lambda n: f"translation_{n}")
    value = factory.Sequence(lambda n: f"translation_value_{n}")


class NewAggregateFactory(factory.Factory):
    class Meta:
        model = NewAggregate

    ordinal = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"label_{n}")
    is_extendable = False
    attributes = factory.Dict({})
    translated = factory.List([FieldTranslationFactory(), FieldTranslationFactory()])


class TranslationFactory(factory.Factory):
    class Meta:
        model = Translation

    ressource_id = factory.Faker("pyuuid4")
    locale = "fr-ca"
    scope = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"translation_{n}")
    value = factory.Sequence(lambda n: f"translation_value_{n}")
    creation_date_utc = factory.Faker("date_time_s", tzinfo=timezone.utc)


class LocalizedAggregateFactory(factory.Factory):
    class Meta:
        model = LocalizedAggregate

    aggregate = factory.SubFactory(AggregateFactory)
    translations = factory.LazyAttribute(
        lambda o: [
            TranslationFactory(
                ressource_id=o.aggregate.project_definition_id,
                locale="fr-ca",
                name=o.aggregate.name,
                scope=o.aggregate.id,
                value=f"{o.aggregate.name} fr",
            ),
            TranslationFactory(
                ressource_id=o.aggregate.project_definition_id,
                locale="fr-ca",
                name=f"{o.aggregate.name}_help_text",
                scope=o.aggregate.id,
                value=f"{o.aggregate.name} fr help",
            ),
            TranslationFactory(
                ressource_id=o.aggregate.project_definition_id,
                locale="en-ca",
                name=o.aggregate.name,
                scope=o.aggregate.id,
                value=f"{o.aggregate.name} en",
            ),
            TranslationFactory(
                ressource_id=o.aggregate.project_definition_id,
                locale="en-ca",
                name=f"{o.aggregate.name}_help_text",
                scope=o.aggregate.id,
                value=f"{o.aggregate.name} en help",
            ),
        ]
    )


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


class ProjectDetailsFactory(factory.Factory):
    class Meta:
        model = ProjectDetails

    id = factory.Faker("pyuuid4")
    name = factory.Sequence(lambda n: f"project{n}")
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


class ProjectNodeFactory(factory.Factory):
    class Meta:
        model = ProjectNode

    id = factory.Faker("pyuuid4")
    project_id = factory.Faker("pyuuid4")
    type_path = factory.List([factory.Faker("pyuuid4"), factory.Faker("pyuuid4")])
    type_id = factory.Faker("pyuuid4")
    type_name = factory.Sequence(lambda n: f"name{n}")
    path = factory.List([factory.Faker("pyuuid4"), factory.Faker("pyuuid4")])
    value = 6
    label = ""

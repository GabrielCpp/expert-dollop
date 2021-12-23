import factory
from expert_dollup.core.domains import *


class ProjectDefinitionNodeFactory(factory.Factory):
    class Meta:
        model = ProjectDefinitionNode

    id = factory.Faker("uuid4")
    project_def_id = factory.Faker("uuid4")
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
    path = []
    creation_date_utc = factory.Faker("date_time")


class ReportInitialSelectionFactory(factory.Factory):
    class Meta:
        model = ReportInitialSelection

    from_object_name = "a"
    from_property_name = "property_a"
    alias_name = "join_a"
    distinct = True


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

    initial_selection = factory.SubFactory(ReportInitialSelectionFactory)
    joins = factory.List([factory.SubFactory(ReportJoinFactory) for _ in range(3)])
    formula_attribute = factory.SubFactory(AttributeBucketFactory)
    datasheet_attribute = factory.SubFactory(AttributeBucketFactory)
    columns = factory.List([])
    group_by = factory.List([])
    order_by = factory.List([])


class ReportColumnFactory(factory.Factory):
    class Meta:
        model = ReportColumn

    name = factory.Sequence(lambda n: f"property_{n}")
    expression = factory.Sequence(lambda n: f"property_{n}*2+1")


class ReportDefinitionFactory(factory.Factory):
    class Meta:
        model = ReportDefinition

    id = factory.Faker("uuid4")
    project_def_id = factory.Faker("uuid4")
    name = factory.Sequence(lambda n: f"report_name_{n}")
    structure = factory.SubFactory(ReportStructureFactory)

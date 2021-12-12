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


class ReportJoinFactory(factory.Factory):
    class Meta:
        model = ReportJoin

    to_object_name = factory.Sequence(lambda n: f"bucket_{n}")
    from_object_name = factory.Sequence(lambda n: f"bucket_{n + 1}")
    join_on_property_name = factory.Sequence(lambda n: f"property_{n}")
    join_type = JoinType.PROPERTY


class ReportStructureFactory(factory.Factory):
    class Meta:
        model = ReportStructure

    initial_selection = factory.SubFactory(ReportJoinFactory)
    joins = factory.List([factory.SubFactory(ReportJoinFactory) for _ in range(3)])


class ReportColumnFactory(factory.Factory):
    class Meta:
        model = ReportColumn

    id = factory.Faker("uuid4")
    name = factory.Sequence(lambda n: f"property_{n}")
    expression = factory.Sequence(lambda n: f"property_{n}*2+1")


class ReportDefinitionFactory(factory.Factory):
    class Meta:
        model = ReportDefinition

    id = factory.Faker("uuid4")
    project_def_id = factory.Faker("uuid4")
    name = factory.Sequence(lambda n: f"property_{n}")
    columns = factory.List([factory.SubFactory(ReportColumnFactory) for _ in range(3)])
    structure = factory.SubFactory(ReportStructureFactory)

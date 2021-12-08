from expert_dollup.core.domains import *
from tests.fixtures.factories_domain import *
from ..fake_db_helpers import FakeDb, DbFixtureGenerator


class SimpleReport(DbFixtureGenerator):
    def __init__(self):
        self._db = FakeDb()

    @property
    def db(self) -> FakeDb:
        return self._db

    def generate(self):
        self.db.add(
            ReportDefinitionFactory(
                name="test report",
                columns=[
                    ReportColumnFactory(
                        name="product_name",
                        expression="product_name_translation.label",
                    ),
                    ReportColumnFactory(
                        name="quantity",
                        expression="truncate(formula.value*factor.value, 2)",
                    ),
                ],
                structure=ReportStructureFactory(
                    initial_selection=ReportJoinFactory(
                        to_object_name="formula",
                        from_object_name="report_formula",
                        join_on_property_name="formula",
                        join_type=JoinType.TABLE_PROPERTY,
                    ),
                    joins=[
                        ReportJoinFactory(
                            to_object_name="products",
                            from_object_name="report_formula",
                            join_on_property_name="formula",
                            join_type=JoinType.TABLE_PROPERTY,
                        ),
                        ReportJoinFactory(
                            to_object_name="project",
                            from_object_name="report_formula",
                            join_on_property_name="formula",
                            join_type=JoinType.TABLE_PROPERTY,
                        ),
                    ],
                ),
            )
        )

        return self

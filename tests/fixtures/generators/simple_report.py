from faker import Faker
from expert_dollup.core.domains import *
from tests.fixtures.factories_domain import ReportDefinitionFactory
from ..fake_db_helpers import FakeDb, DbFixtureGenerator


class SimpleReport(DbFixtureGenerator):
    def __init__(self):
        self._db = FakeDb()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)

    @property
    def db(self) -> FakeDb:
        return self._db

    def generate(self):
        self.db.add(
            ReportDefinitionFactory(
                name="test report",
                columns=[
                    ReportColumn(
                        name="product_name",
                        expression="product_name_translation.label",
                    ),
                    ReportColumn(
                        name="quantity",
                        expression="truncate(formula.value*factor.value, 2)",
                    ),
                ],
                structure=ReportStructure(
                    initial_selection=ReportJoin(
                        to_object_name="formula",
                        from_object_name="report_formula",
                        join_on_property_name="formula",
                        join_type=JoinType.TABLE_PROPERTY,
                    ),
                    joins=[
                        ReportJoin(
                            to_object_name="products",
                            from_object_name="report_formula",
                            join_on_property_name="formula",
                            join_type=JoinType.TABLE_PROPERTY,
                        ),
                        ReportJoin(
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
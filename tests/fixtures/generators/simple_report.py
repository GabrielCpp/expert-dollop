from faker import Faker
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeDb, DbFixtureGenerator


class SimpleReport(DbFixtureGenerator):
    def __init__(self):
        self.db = FakeDb()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)

    def generate(self):
        return self

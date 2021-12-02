from uuid import uuid4, UUID
from datetime import timezone
from faker import Faker
from typing import List
from pydantic import BaseModel
from expert_dollup.core.domains import *
from ..fake_db_helpers import FakeExpertDollupDb as Tables


class SimpleReport:
    def __init__(self):
        self.tables = Tables()
        self.fake = Faker()
        self.fake.seed_instance(seed=1)

    def generate(self):
        return self

    @property
    def model(self) -> Tables:
        return Tables(
            project_definitions=self.project_definitions,
            project_definition_nodes=self.project_definition_nodes,
            translations=self.tanslations,
        )
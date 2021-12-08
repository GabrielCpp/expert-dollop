import pytest
from typing import List
from uuid import UUID
from expert_dollup.app.dtos import *
from ..fixtures import *


@pytest.mark.asyncio
async def test_given_report_definition(ac, db_helper: DbFixtureHelper):
    fake_db = await db_helper.load_fixtures(SimpleReport)

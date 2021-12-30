import pytest
from typing import List
from uuid import UUID
from expert_dollup.app.dtos import *
from expert_dollup.core.units import *
from ..fixtures import *


@pytest.mark.asyncio
async def test_given_report_definition(ac, db_helper: DbFixtureHelper):
    runner = FlowRunner()

    @runner.step
    async def project_checkbox_toogle_visibility_root_collection():
        response = await ac.post(
            f"/api/project/{project.id}/container/collection",
            data=ProjectNodeCollectionTargetDto(
                parent_node_id=None, collection_type_id=root_b_node.id
            ).json(),
        )
        assert response.status_code == 200, response.text

    await runner.run()

import pytest
from ..fixtures import *
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.infra.expert_dollup_db import *


@pytest.mark.asyncio
async def test_datasheet(ac, mini_datasheet):
    datasheet = DatasheetFactoryDto()
    response = await ac.post("/api/datasheet", datasheet.json())
    assert response.status_code == 200, response.json()

    response = await ac.get(f"/api/datasheet/{datasheet.id}/elements", datasheet.json())
    assert response.status_code == 200, response.json()

    # Check all element are there

    datasheet_element_child = DatasheetElementDtoFactory()

    response = await ac.post(
        f"/api/datasheet/{datasheet.id}/element_definition/{datasheet_element_child.element_def_id}",
        datasheet_element_child.json(),
    )
    assert response.status_code == 200, response.json()

    response = await ac.get(
        f"/api/datasheet/{datasheet.id}/element/{datasheet_element_child.element_def_id}/{datasheet_element_child.child_element_reference}",
        datasheet_element_child.json(),
    )
    assert response.status_code == 200, response.json()

    new_child_element = unwrap(response, DatasheetElementDto)
    assert new_child_element == datasheet_element_child

    response = await ac.post(f"/api/datasheet/{datasheet.id}/clone")
    assert response.status_code == 200, response.json()

    cloned_datasheet = unwrap(response, DatasheetDto)
    assert cloned_datasheet =  datasheet


# add datasheet from definition
# add child element
# clone datasheet

# delete datasheet
# delete child element
# set datasheet property

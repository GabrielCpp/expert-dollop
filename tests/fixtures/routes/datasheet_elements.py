from uuid import UUID
from typing import List
from expert_dollup.app.dtos import *
from ..integrated_test_client import IntegratedTestClient


async def replace_datasheet_element(
    ac: IntegratedTestClient,
    datasheet_id: UUID,
    element_id: UUID,
    new_element: NewDatasheetDto,
):
    new_child_element = await ac.put_json(
        f"/api/datasheets/{datasheet_id}/elements/{element_id}",
        new_element,
        unwrap_with=DatasheetElementDto,
    )
    return new_child_element


async def patch_datasheet_element_values(
    ac: IntegratedTestClient,
    datasheet_id: UUID,
    element_id: UUID,
    attributes: List[AttributeDto],
):
    element = await ac.patch_json(
        f"/api/datasheets/{datasheet_id}/elements/{element_id}/values",
        attributes,
        unwrap_with=DatasheetElementDto,
    )
    return element


async def create_datasheet_element(
    ac: IntegratedTestClient,
    datasheet_id: UUID,
    new_element: NewDatasheetElementDto,
):
    return await ac.post_json(
        f"/api/datasheets/{datasheet_id}/elements",
        new_element,
        unwrap_with=DatasheetElementDto,
    )


async def delete_datasheet_element(
    ac: IntegratedTestClient, datasheet_id: UUID, element_id: UUID
):
    await ac.delete_json(f"/api/datasheets/{datasheet_id}/elements/{element_id}")


async def get_datasheet_element(
    ac: IntegratedTestClient,
    datasheet_id: UUID,
    element_id: UUID,
    expected_status_code=200,
):
    return await ac.get_json(
        f"/api/datasheets/{datasheet_id}/elements/{element_id}",
        unwrap_with=DatasheetElementDto if expected_status_code == 200 else dict,
        expected_status_code=expected_status_code,
    )


async def get_paginated_datasheet_element_by_aggregate(
    ac: IntegratedTestClient, datasheet_dto: DatasheetDto, aggregate_id: UUID
):
    elements_page_dto = await ac.get_json(
        f"/api/datasheets/{datasheet_dto.id}/elements?aggregate_id={aggregate_id}",
        unwrap_with=bind_page_dto(DatasheetElementDto),
    )
    return elements_page_dto


async def get_paginated_datasheet_elements(
    ac: IntegratedTestClient, datasheet_dto: DatasheetDto
):
    elements_page_dto = await ac.get_json(
        f"/api/datasheets/{datasheet_dto.id}/elements",
        unwrap_with=bind_page_dto(DatasheetElementDto),
    )
    assert len(elements_page_dto.results) == 2
    return elements_page_dto

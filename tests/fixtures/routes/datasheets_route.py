from uuid import UUID
from ..integrated_test_client import IntegratedTestClient
from expert_dollup.app.dtos import *


async def get_datasheet(ac: IntegratedTestClient, datasheet_id: UUID):
    datasheet_dto = await ac.post_json(
        "/api/datasheets/{datasheet_id}", unwrap_with=DatasheetDto
    )
    return datasheet_dto


async def create_datasheet(ac: IntegratedTestClient, new_datasheet: NewDatasheetDto):
    datasheet_dto = await ac.post_json(
        "/api/datasheets", new_datasheet, unwrap_with=DatasheetDto
    )
    return datasheet_dto


async def delete_datasheet(ac: IntegratedTestClient, datasheet_id: UUID):
    await ac.delete_json(f"/api/datasheets/{datasheet_id}")
    await ac.get_json(f"/api/datasheets/{datasheet_id}", expected_status_code=404)


async def clone_datasheet(ac: IntegratedTestClient, datasheet_dto: DatasheetDto):
    datasheet_clone_target = CloningDatasheetDto(
        target_datasheet_id=datasheet_dto.id, clone_name="Renamed datasheet"
    )
    cloned_datasheet_dto = await ac.post_json(
        f"/api/datasheets/{datasheet_dto.id}/clone",
        datasheet_clone_target,
        unwrap_with=DatasheetDto,
    )
    assert cloned_datasheet_dto.name == datasheet_clone_target.clone_name

    actual_datasheet_dto = await ac.get_json(
        f"/api/datasheets/{cloned_datasheet_dto.id}", unwrap_with=DatasheetDto
    )
    assert actual_datasheet_dto == cloned_datasheet_dto

    return cloned_datasheet_dto

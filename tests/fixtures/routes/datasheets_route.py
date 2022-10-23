from uuid import UUID
from ..integrated_test_client import IntegratedTestClient
from expert_dollup.app.dtos import *


async def create_datasheet(ac, new_datasheet: NewDatasheetDto):
    datasheet_dto = await ac.post_json(
        "/api/datasheets", new_datasheet, unwrap_with=DatasheetDto
    )
    return datasheet_dto

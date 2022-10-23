from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional, Dict, List
from expert_dollup.shared.database_services import Paginator
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.usecases import DatasheetElementUseCase
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.get("/datasheets/{datasheet_id}/elements")
async def find_datasheet_elements(
    datasheet_id: UUID,
    limit: int = Query(alias="limit", default=100),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    handler: PageHandlerProxy = Depends(Inject(PageHandlerProxy)),
    paginator=Depends(Inject(Paginator[DatasheetElement])),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:get"])),
):
    return await handler.use_paginator(paginator).handle(
        DatasheetElementDto,
        DatasheetElementFilter(datasheet_id=datasheet_id),
        limit,
        next_page_token,
    )


@router.get("/datasheets/{datasheet_id}/elements")
async def find_paginated_datasheet_elements(
    datasheet_id: UUID,
    limit: int = Query(alias="limit", default=100),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    handler=Depends(Inject(PageHandlerProxy)),
    paginator=Depends(Inject(Paginator[DatasheetElement])),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:get"])),
):
    return await handler.use_paginator(paginator).handle(
        DatasheetElementDto,
        DatasheetElementFilter(datasheet_id=datasheet_id),
        limit,
        next_page_token,
    )


@router.get("/datasheets/{datasheet_id}/elements/{datasheet_element_id}")
async def find_datasheet_element(
    datasheet_id: UUID,
    datasheet_element_id: UUID,
    request_handler: RequestHandler = Depends(Inject(RequestHandler)),
    usecase: DatasheetElementUseCase = Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:get"])),
):
    return await request_handler.do_handle(
        usecase.find,
        MappingChain(domain=DatasheetElement, dto=DatasheetElementDto),
        datasheet_element_id=datasheet_element_id,
        datasheet_id=datasheet_id,
    )


@router.put("/datasheets/{datasheet_id}/elements/{datasheet_element_id}")
async def update_datasheet_element_properties(
    datasheet_id: UUID,
    datasheet_element_id: UUID,
    replacement: NewDatasheetElementDto,
    request_handler: RequestHandler = Depends(Inject(RequestHandler)),
    usecase: DatasheetElementUseCase = Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:update"])),
):
    return await request_handler.do_handle(
        usecase.update,
        MappingChain(domain=DatasheetElement, dto=DatasheetElementDto),
        datasheet_id=datasheet_id,
        datasheet_element_id=datasheet_element_id,
        replacement=MappingChain(
            value=replacement, dto=NewDatasheetElementDto, domain=NewDatasheetElement
        ),
    )


@router.post("/datasheets/{datasheet_id}/elements")
async def add_datasheet_element(
    datasheet_id: UUID,
    new_element: NewDatasheetElementDto,
    request_handler: RequestHandler = Depends(Inject(RequestHandler)),
    usecase: DatasheetElementUseCase = Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:update"])),
):
    return await request_handler.do_handle(
        usecase.add,
        MappingChain(domain=DatasheetElement, dto=DatasheetElementDto),
        datasheet_id=datasheet_id,
        user=user,
        new_element=MappingChain(
            value=new_element, domain=NewDatasheetElement, dto=NewDatasheetElementDto
        ),
    )


@router.put("/datasheets/{datasheet_id}/elements")
async def batch_update_datasheet_elements_attributes(
    datasheet_id: UUID,
    updates: List[DatasheetElementUpdateDto],
    usecase: DatasheetElementUseCase = Depends(Inject(DatasheetElementUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:update"])),
):
    return await handler.do_handle(
        usecase.batch_update_values,
        MappingChain(dto=List[DatasheetElementUpdateDto]),
        datasheet_id=datasheet_id,
        updates=MappingChain(
            value=updates,
            dto=List[DatasheetElementUpdateDto],
            domain=List[DatasheetElementUpdate],
        ),
    )


@router.delete("/datasheets/{datasheet_id}/elements/{datasheet_element_id}")
async def delete_datasheet_element_from_collection(
    datasheet_id: UUID,
    datasheet_element_id: UUID,
    usecase: DatasheetElementUseCase = Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:delete"])),
):
    await usecase.delete(datasheet_id, datasheet_element_id)

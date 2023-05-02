from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional, Dict, List
from expert_dollup.shared.database_services import Paginator
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.services import DatasheetElementUseCase
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.get("/datasheets/{datasheet_id}/elements")
async def find_paginated_datasheet_elements(
    datasheet_id: UUID,
    limit: int = Query(alias="limit", default=100),
    aggregate_id: UUID = Query(alias="aggregate_id", default=None),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    handler: PageHandlerProxy = Depends(Inject(PageHandlerProxy)),
    paginator=Depends(Inject(Paginator[DatasheetElement])),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:get"])),
):
    query_filter = (
        DatasheetElementFilter(datasheet_id=datasheet_id)
        if aggregate_id is None
        else DatasheetElementFilter(
            datasheet_id=datasheet_id, aggregate_id=aggregate_id
        )
    )

    return await handler.use_paginator(paginator).handle(
        DatasheetElementDto,
        query_filter,
        limit,
        next_page_token,
    )


@router.get("/datasheets/{datasheet_id}/elements/{element_id}")
async def find_datasheet_element(
    datasheet_id: UUID,
    element_id: UUID,
    request_handler: RequestHandler = Depends(Inject(RequestHandler)),
    usecase: DatasheetElementUseCase = Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:get"])),
):
    return await request_handler.do_handle(
        usecase.find,
        MappingChain(domain=DatasheetElement, dto=DatasheetElementDto),
        datasheet_id=datasheet_id,
        element_id=element_id,
    )


@router.put("/datasheets/{datasheet_id}/elements/{element_id}")
async def update_datasheet_element_properties(
    datasheet_id: UUID,
    element_id: UUID,
    replacement: NewDatasheetElementDto,
    request_handler: RequestHandler = Depends(Inject(RequestHandler)),
    usecase: DatasheetElementUseCase = Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:update"])),
):
    return await request_handler.do_handle(
        usecase.update,
        MappingChain(domain=DatasheetElement, dto=DatasheetElementDto),
        datasheet_id=datasheet_id,
        datasheet_element_id=element_id,
        user=user,
        replacement=MappingChain(
            value=replacement, dto=NewDatasheetElementDto, domain=NewDatasheetElement
        ),
    )


@router.patch("/datasheets/{datasheet_id}/elements/{element_id}/values")
async def patch_datasheet_element_values(
    datasheet_id: UUID,
    element_id: UUID,
    attributes: List[AttributeDto],
    request_handler: RequestHandler = Depends(Inject(RequestHandler)),
    usecase: DatasheetElementUseCase = Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:update"])),
):
    return await request_handler.do_handle(
        usecase.update_values,
        MappingChain(domain=DatasheetElement, dto=DatasheetElementDto),
        datasheet_id=datasheet_id,
        datasheet_element_id=element_id,
        user=user,
        attributes=MappingChain(
            dto=List[AttributeDto], domain=List[Attribute], value=attributes
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


@router.delete("/datasheets/{datasheet_id}/elements/{element_id}")
async def delete_datasheet_element_from_collection(
    datasheet_id: UUID,
    element_id: UUID,
    usecase: DatasheetElementUseCase = Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:delete"])),
):
    await usecase.delete(datasheet_id, element_id)

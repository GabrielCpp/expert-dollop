from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional, Dict
from expert_dollup.shared.database_services import Paginator
from expert_dollup.core.usecases import DatasheetElementUseCase
from expert_dollup.shared.starlette_injection import *
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


@router.get(
    "/datasheets/{datasheet_id}/element/{element_def_id}/{child_element_reference}"
)
async def find_datasheet_element(
    datasheet_id: UUID,
    element_def_id: UUID,
    child_element_reference: UUID,
    request_handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:get"])),
):
    return await request_handler.handle(
        usecase.find_datasheet_element,
        DatasheetElementId(
            datasheet_id=datasheet_id,
            element_def_id=element_def_id,
            child_element_reference=child_element_reference,
        ),
        MappingChain(
            out_domain=DatasheetElement,
            out_dto=DatasheetElementDto,
        ),
    )


@router.put(
    "/datasheets/{datasheet_id}/element/{element_def_id}/{child_element_reference}"
)
async def update_datasheet_element_properties(
    datasheet_id: UUID,
    element_def_id: UUID,
    child_element_reference: UUID,
    properties: Dict[str, PrimitiveUnion],
    request_handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:update"])),
):
    return await request_handler.forward(
        usecase.update_datasheet_element_properties,
        {
            "id": DatasheetElementId(
                datasheet_id=datasheet_id,
                element_def_id=element_def_id,
                child_element_reference=child_element_reference,
            ),
            "properties": properties,
        },
        MappingChain(
            out_domain=DatasheetElement,
            out_dto=DatasheetElementDto,
        ),
    )


@router.post("/datasheets/{datasheet_id}/element_collection/{element_def_id}")
async def add_datasheet_element_to_collection(
    datasheet_id: UUID,
    element_def_id: UUID,
    properties: Dict[str, PrimitiveUnion],
    request_handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:update"])),
):
    return await request_handler.forward(
        usecase.add_collection_item,
        dict(
            datasheet_id=datasheet_id,
            element_def_id=element_def_id,
            properties=properties,
        ),
        MappingChain(
            out_domain=DatasheetElement,
            out_dto=DatasheetElementDto,
        ),
    )


@router.delete(
    "/datasheets/{datasheet_id}/element_collection/{element_def_id}/{child_element_reference}"
)
async def delete_datasheet_element_from_collection(
    datasheet_id: UUID,
    element_def_id: UUID,
    child_element_reference: UUID,
    usecase=Depends(Inject(DatasheetElementUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:delete"])),
):
    await usecase.delete_element(
        DatasheetElementId(
            datasheet_id=datasheet_id,
            element_def_id=element_def_id,
            child_element_reference=child_element_reference,
        )
    )

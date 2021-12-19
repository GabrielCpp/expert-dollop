from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    MappingChain,
    HttpPageHandler,
)
from expert_dollup.core.usecases import DatasheetDefinitionElementUseCase
from expert_dollup.core.domains import (
    DatasheetDefinitionElement,
    DatasheetDefinitionElementFilter,
)
from expert_dollup.app.dtos import DatasheetDefinitionElementDto

router = APIRouter()


@router.get("/datasheet_definition_element/{datasheet_definition_element_id}")
async def find_datasheet_definition_element_by_id(
    datasheet_definition_element_id: UUID,
    usecase=Depends(Inject(DatasheetDefinitionElementUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id,
        datasheet_definition_element_id,
        MappingChain(out_dto=DatasheetDefinitionElementDto),
    )


@router.get("/datasheet_definition/{datasheet_definition_id}/elements")
async def find_datasheet_definition_elements(
    datasheet_definition_id: UUID,
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = Query(alias="limit", default=100),
    handler=Depends(Inject(HttpPageHandler)),
):
    return await handler.handle(
        DatasheetDefinitionElementFilter(datasheet_def_id=datasheet_definition_id),
        limit,
        next_page_token,
    )


@router.post("/datasheet_definition_element")
async def add_datasheet_definition_element(
    datasheet_definition: DatasheetDefinitionElementDto,
    usecase=Depends(Inject(DatasheetDefinitionElementUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.add,
        datasheet_definition,
        MappingChain(
            dto=DatasheetDefinitionElementDto,
            domain=DatasheetDefinitionElement,
            out_dto=DatasheetDefinitionElementDto,
        ),
    )


@router.put("/datasheet_definition_element")
async def update_datasheet_definition_element(
    datasheet_definition: DatasheetDefinitionElementDto,
    usecase=Depends(Inject(DatasheetDefinitionElementUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.update,
        datasheet_definition,
        MappingChain(
            dto=DatasheetDefinitionElementDto,
            domain=DatasheetDefinitionElement,
            out_dto=DatasheetDefinitionElementDto,
        ),
    )


@router.delete("/datasheet_definition_element/{datasheet_definition_element_id}")
async def delete_datasheet_definition_element_by_id(
    datasheet_definition_element_id: UUID,
    usecase=Depends(Inject(DatasheetDefinitionElementUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await usecase.delete_by_id(datasheet_definition_element_id)

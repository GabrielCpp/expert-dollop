from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from expert_dollup.shared.database_services import Paginator
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    MappingChain,
    HttpPageHandler,
    Inject,
)
from expert_dollup.core.usecases import DatasheetDefinitionElementUseCase
from expert_dollup.core.domains import (
    DatasheetDefinitionElement,
    DatasheetDefinitionElementFilter,
)
from expert_dollup.app.dtos import DatasheetDefinitionElementDto

router = APIRouter()


@router.get(
    "/definitions/{project_definition_id}/datasheet_elements/{datasheet_definition_element_id}"
)
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


@router.get("/definitions/{project_definition_id}/datasheet_elements")
async def find_datasheet_definition_elements(
    project_definition_id: UUID,
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = Query(alias="limit", default=100),
    handler=Depends(Inject(HttpPageHandler[Paginator[DatasheetDefinitionElement]])),
):
    return await handler.handle(
        DatasheetDefinitionElementDto,
        DatasheetDefinitionElementFilter(project_definition_id=project_definition_id),
        limit,
        next_page_token,
    )


@router.post("/definitions/{project_definition_id}/datasheet_elements")
async def add_datasheet_definition_element(
    project_definition_id: UUID,
    datasheet_definition_element: DatasheetDefinitionElementDto,
    usecase=Depends(Inject(DatasheetDefinitionElementUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.add,
        datasheet_definition_element,
        MappingChain(
            dto=DatasheetDefinitionElementDto,
            domain=DatasheetDefinitionElement,
            out_dto=DatasheetDefinitionElementDto,
        ),
    )


@router.put("/definitions/{project_definition_id}/datasheet_elements")
async def update_datasheet_definition_element(
    project_definition_id: UUID,
    project_definition: DatasheetDefinitionElementDto,
    usecase=Depends(Inject(DatasheetDefinitionElementUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.update,
        project_definition,
        MappingChain(
            dto=DatasheetDefinitionElementDto,
            domain=DatasheetDefinitionElement,
            out_dto=DatasheetDefinitionElementDto,
        ),
    )


@router.delete(
    "/definitions/{project_definition_id}/datasheet_elements/{datasheet_definition_element_id}"
)
async def delete_datasheet_definition_element_by_id(
    project_definition_id: UUID,
    datasheet_definition_element_id: UUID,
    usecase=Depends(Inject(DatasheetDefinitionElementUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await usecase.delete_by_id(datasheet_definition_element_id)

from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.starlette_injection import RequestHandler, MappingChain
from expert_dollup.core.domains import DatasheetDefinition
from expert_dollup.app.dtos import DatasheetDefinitionDto
from expert_dollup.core.usecases import DatasheetDefinitionUseCase
from expert_dollup.app.jwt_auth import CanPerformOnRequired, CanPerformRequired

router = APIRouter()


@router.get("/datasheet_definition/{datasheet_definition_id}")
async def find_datasheet_definition_by_id(
    datasheet_definition_id: UUID,
    usecase=Depends(Inject(DatasheetDefinitionUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id,
        datasheet_definition_id,
        MappingChain(out_dto=DatasheetDefinitionDto),
    )


@router.post("/datasheet_definition")
async def add_datasheet_definition(
    datasheet_definition: DatasheetDefinitionDto,
    usecase=Depends(Inject(DatasheetDefinitionUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired("datasheet_definition:create")),
):
    return await handler.forward_mapped(
        usecase.add,
        dict(domain=datasheet_definition, user=user),
        MappingChain(out_dto=DatasheetDefinitionDto),
        map_keys=dict(
            domain=MappingChain(dto=DatasheetDefinitionDto, domain=DatasheetDefinition)
        ),
    )


@router.put("/datasheet_definition")
async def update_datasheet_definition(
    datasheet_definition: DatasheetDefinitionDto,
    usecase=Depends(Inject(DatasheetDefinitionUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.update,
        datasheet_definition,
        MappingChain(
            dto=DatasheetDefinitionDto,
            domain=DatasheetDefinition,
            out_dto=DatasheetDefinitionDto,
        ),
    )


@router.delete("/datasheet_definition/{datasheet_definition_id}")
async def delete_datasheet_definition_by_id(
    datasheet_definition_id: UUID,
    usecase=Depends(Inject(DatasheetDefinitionUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await usecase.delete_by_id(datasheet_definition_id)

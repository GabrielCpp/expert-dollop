from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.app.dtos import ProjectDefinitionDto
from expert_dollup.core.domains.project_definition import ProjectDefinition
from expert_dollup.core.usecases import ProjectDefinitonUseCase
from expert_dollup.infra.providers import ValueTypeProvider
from expert_dollup.core.exceptions import RessourceNotFound

router = APIRouter()


@router.get("/project_definition/{id}")
async def find_project_definition(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id, id, MappingChain(out_dto=ProjectDefinitionDto)
    )


@router.post("/project_definition")
async def create_project_definition(
    project_definition: ProjectDefinitionDto,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.handle(
        usecase.add,
        project_definition,
        MappingChain(
            dto=ProjectDefinitionDto,
            domain=ProjectDefinition,
            out_dto=ProjectDefinitionDto,
        ),
    )


@router.put("/project_definition")
async def update_project_definition(
    project_definition: ProjectDefinitionDto,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.handle(
        usecase.update,
        project_definition,
        MappingChain(
            dro=ProjectDefinitionDto,
            domain=ProjectDefinition,
            out_dto=ProjectDefinitionDto,
        ),
    )


@router.delete("/project_definition/{id}")
async def delete_project_definition(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    await usecase.remove_by_id(id)


@router.get("/value_type_schema/{value_type}")
def get_value_type_schema_from_provider(
    value_type: str, provider=Depends(Inject(ValueTypeProvider))
):
    schema_per_type = provider.get_schema_per_type()

    if not value_type in schema_per_type:
        raise RessourceNotFound()

    return schema_per_type
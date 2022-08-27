from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    MappingChain,
    Inject,
    CanPerformOnRequired,
    CanPerformRequired,
)
from expert_dollup.app.dtos import ProjectDefinitionDto
from expert_dollup.core.domains.project_definition import ProjectDefinition
from expert_dollup.core.usecases import ProjectDefinitonUseCase


router = APIRouter()


@router.get("/definitions/{project_definition_id}")
async def find_project_definition(
    project_definition_id: UUID,
    usecase: ProjectDefinitonUseCase = Depends(Inject(ProjectDefinitonUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:read"])
    ),
):
    return await handler.handle(
        usecase.find_by_id,
        project_definition_id,
        MappingChain(out_dto=ProjectDefinitionDto),
    )


@router.post("/definitions")
async def create_project_definition(
    project_definition: ProjectDefinitionDto,
    usecase: ProjectDefinitonUseCase = Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired("project_definition:create")),
):
    return await request_handler.forward_mapped(
        usecase.add,
        dict(domain=project_definition, user=user),
        MappingChain(out_dto=ProjectDefinitionDto),
        map_keys=dict(
            domain=MappingChain(
                dto=ProjectDefinitionDto,
                domain=ProjectDefinition,
            ),
        ),
    )


@router.put("/definitions/{project_definition_id}")
async def update_project_definition(
    project_definition: ProjectDefinitionDto,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
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


@router.delete("/definitions/{project_definition_id}")
async def delete_project_definition(
    project_definition_id: UUID,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:delete"])
    ),
):
    await usecase.delete_by_id(project_definition_id)

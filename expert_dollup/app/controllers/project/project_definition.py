from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import RequestHandler, MappingChain
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.app.dtos import ProjectDefinitionDto
from expert_dollup.core.domains.project_definition import ProjectDefinition
from expert_dollup.core.usecases import ProjectDefinitonUseCase
from expert_dollup.app.jwt_auth import CanPerformOnRequired, CanPerformRequired

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
    await usecase.delete_by_id(id)

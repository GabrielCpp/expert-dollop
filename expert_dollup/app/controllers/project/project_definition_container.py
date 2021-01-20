from fastapi import APIRouter, Depends, Query
from typing import Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.app.dtos import (
    ProjectDefinitionContainerDto,
    ProjectDefinitionContainerPageDto,
)
from expert_dollup.core.domains import ProjectDefinitionContainer
from expert_dollup.core.usecases import ProjectDefinitonContainerUseCase


router = APIRouter()


@router.get("/project_definition_container/{id}")
async def get_project_definition_container(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id, id, MappingChain(out_dto=ProjectDefinitionContainerDto)
    )


@router.post("/project_definition_container")
async def create_project_definition_container(
    project_definition_container: ProjectDefinitionContainerDto,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.handle(
        usecase.add,
        project_definition_container,
        MappingChain(
            dto=ProjectDefinitionContainerDto,
            domain=ProjectDefinitionContainer,
            out_dto=ProjectDefinitionContainerDto,
        ),
    )


@router.put("/project_definition_container")
async def replace_project_definition_container(
    project_definition_container: ProjectDefinitionContainerDto,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.handle(
        usecase.update,
        project_definition_container,
        MappingChain(
            dto=ProjectDefinitionContainerDto,
            domain=ProjectDefinitionContainer,
            out_dto=ProjectDefinitionContainerDto,
        ),
    )


@router.delete("/project_definition_container/{id}")
async def delete_project_definition_container(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler)),
):
    await usecase.remove_by_id(id)


@router.get("/{project_def_id}/project_container_definitions")
async def get_project_definition_container_by_project(
    project_def_id: UUID,
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = Query(alias="limit", default=10),
):
    query = PaginatedRessource[UUID](
        next_page_token=next_page_token,
        limit=limit,
        query=project_def_id,
    )

    return await request_handler.handle(
        usecase.find_by_project_definition,
        query,
        MappingChain(
            out_dto=ProjectDefinitionContainerPageDto,
        ),
    )

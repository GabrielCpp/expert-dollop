import structlog
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
from expert_dollup.shared.database_services import Page

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


@router.get("/{project_def_id}/project_definition_containers")
async def get_project_definition_container_by_project(
    project_def_id: UUID,
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    limit: int = Query(alias="limit", default=100),
    request_handler=Depends(Inject(RequestHandler)),
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
):
    return await request_handler.forward(
        usecase.find_project_containers,
        dict(
            next_page_token=next_page_token,
            limit=limit,
            project_def_id=project_def_id,
        ),
        MappingChain(
            out_domain=Page[ProjectDefinitionContainer],
            out_dto=ProjectDefinitionContainerPageDto,
        ),
    )

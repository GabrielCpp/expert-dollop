from fastapi import APIRouter, Depends
from uuid import UUID
from predykt.shared.starlette_injection import Inject
from predykt.shared.handlers import RequestHandler
from predykt.app.dtos import ProjectDefinitionContainerDto
from predykt.core.domains import ProjectDefinitionContainer
from predykt.core.usecases import ProjectDefinitonContainerUseCase


router = APIRouter()


@router.get("/project_definition_container/{id}")
async def get_project_definition(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await handler.handle_id_with_result(id, usecase.find_by_id, ProjectDefinitionContainerDto)


@router.post("/project_definition_container")
async def create_project_definition(
    project_definition_container: ProjectDefinitionContainerDto,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(project_definition_container, ProjectDefinitionContainerDto, ProjectDefinitionContainer, usecase.add)


@router.put("/project_definition_container")
async def replace_project_definition(
    project_definition_container: ProjectDefinitionContainerDto,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(project_definition_container, ProjectDefinitionContainerDto, ProjectDefinitionContainer, usecase.update)


@router.delete("/project_definition_container/{id}")
async def delete_project_definition(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonContainerUseCase)),
    request_handler=Depends(Inject(RequestHandler))
):
    await usecase.delete_by_id(id)

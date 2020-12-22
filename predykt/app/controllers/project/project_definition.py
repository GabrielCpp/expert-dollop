from fastapi import APIRouter, Depends
from uuid import UUID
from predykt.shared.handlers import RequestHandler
from predykt.shared.starlette_injection import Inject
from predykt.app.dtos import ProjectDefinitionDto
from predykt.core.domains.project_definition import ProjectDefinition
from predykt.core.usecases import ProjectDefinitonUseCase


router = APIRouter()


@router.get("/project_definition/{id}")
async def get_project_definition(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await handler.handle_id_with_result(id, usecase.find_by_id, ProjectDefinitionDto)


@router.post("/project_definition")
async def create_project_definition(
    project_definition: ProjectDefinitionDto,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(project_definition, ProjectDefinitionDto, ProjectDefinition, usecase.add)


@router.put("/project_definition")
async def update_project_definition(
    project_definition: ProjectDefinitionDto,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(project_definition, ProjectDefinitionDto, ProjectDefinition, usecase.update)


@router.delete("/project_definition/{id}")
async def delete_project_definition(
    id: UUID,
    usecase=Depends(Inject(ProjectDefinitonUseCase)),
    request_handler=Depends(Inject(RequestHandler))
):
    await usecase.remove_by_id(id)

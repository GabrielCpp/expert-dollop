from fastapi import APIRouter, Depends
from uuid import UUID
from predykt.shared.handlers import RequestHandler
from predykt.shared.starlette_injection import Inject
from predykt.app.dtos import ProjectDefinitionDto
from predykt.core.domains.project_definition import ProjectDefinition
from predykt.infra.services import ProjectDefinitionService
from predykt.core.usecases import ProjectDefinitonUseCase


router = APIRouter()


@router.get("/project_definition/{id}")
async def get_project_definition(
    id: UUID,
    project_definition_usecase=Depends(Inject(ProjectDefinitonUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await handler.handle_id_with_result(id, project_definition_usecase.find_by_id, ProjectDefinitionDto)


@router.post("/project_definition")
async def create_project_definition(
    project_definition: ProjectDefinitionDto,
    project_definition_service=Depends(Inject(ProjectDefinitionService)),
    request_handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(project_definition, ProjectDefinitionDto, ProjectDefinition, project_definition_service.insert)


@router.put("/project_definition")
async def update_project_definition(
    project_definition: ProjectDefinitionDto,
    project_definition_service=Depends(Inject(ProjectDefinitionService)),
    request_handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(project_definition, ProjectDefinitionDto, ProjectDefinition, project_definition_service.update)


@router.delete("/project_definition/{id}")
async def delete_project_definition(
    id: UUID,
    project_definition_service=Depends(Inject(ProjectDefinitionService)),
    request_handler=Depends(Inject(RequestHandler))
):
    await project_definition_service.delete_by_id(id)

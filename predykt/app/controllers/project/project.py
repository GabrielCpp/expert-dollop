from fastapi import APIRouter, Depends
from uuid import UUID
from predykt.shared.starlette_injection import Inject
from predykt.shared.handlers import RequestHandler
from predykt.app.dtos import ProjectDto
from predykt.core.domains import Project
from predykt.core.usecases import ProjectUseCase

router = APIRouter()


@router.get("/project/{id}")
async def get_project(
    id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await handler.handle_id_with_result(id, usecase.find_by_id, ProjectDto)


@router.post("/project")
async def create_project(
    project: ProjectDto,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(project, ProjectDto, Project, usecase.insert)


@router.put("/project")
async def update_project(
    project: ProjectDto,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    return await request_handler.handle(project, ProjectDto, Project, usecase.update)


@router.delete("/project/{id}")
async def delete_project(
    id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler))
):
    await usecase.delete_by_id(id)

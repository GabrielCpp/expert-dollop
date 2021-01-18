from fastapi import APIRouter, Depends
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.app.dtos import ProjectDto
from expert_dollup.core.domains import Project
from expert_dollup.core.usecases import ProjectUseCase

router = APIRouter()


@router.get("/project/{id}")
async def get_project(
    id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id, id, MappingChain(out_dto=ProjectDto)
    )


@router.post("/project")
async def create_project(
    project: ProjectDto,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.handle(
        usecase.insert,
        project,
        MappingChain(dto=ProjectDto, domain=Project, out_dto=ProjectDto),
    )


@router.put("/project")
async def update_project(
    project: ProjectDto,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await request_handler.handle(
        usecase.update,
        project,
        MappingChain(dto=ProjectDto, domain=Project, out_dto=ProjectDto),
    )


@router.delete("/project/{id}")
async def delete_project(
    id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    await usecase.delete_by_id(id)

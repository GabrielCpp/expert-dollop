from fastapi import APIRouter, Depends, Query
from uuid import UUID, uuid4
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    MappingChain,
    CanPerformOnRequired,
    CanPerformRequired,
    Inject,
)
from expert_dollup.app.dtos import ProjectDetailsDto, ProjectDetailsInputDto
from expert_dollup.core.domains import ProjectDetails
from expert_dollup.core.usecases import ProjectUseCase

router = APIRouter()


@router.get("/projects/{project_id}")
async def find_project_details(
    project_id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("project_id", ["project:get"])),
):
    return await handler.handle(
        usecase.find_by_id, project_id, MappingChain(out_dto=ProjectDetailsDto)
    )


@router.post("/projects")
async def create_project(
    project: ProjectDetailsInputDto,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired("project:create")),
):
    return await handler.forward_mapped(
        usecase.add,
        dict(project_details=project, user=user),
        MappingChain(out_dto=ProjectDetailsDto),
        map_keys=dict(
            project_details=MappingChain(
                dto=ProjectDetailsInputDto,
                domain=ProjectDetails,
            ),
        ),
    )


@router.post("/projects/{project_id}/clone")
async def clone_project(
    project_id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_id", ["project:get"], ["project:clone"])
    ),
):
    return await handler.forward(
        usecase.clone,
        dict(project_id=project_id, user=user),
        MappingChain(out_dto=ProjectDetailsDto),
    )


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    user=Depends(CanPerformOnRequired("project_id", ["project:delete"])),
):
    await usecase.delete_by_id(project_id)

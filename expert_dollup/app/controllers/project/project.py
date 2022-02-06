from fastapi import APIRouter, Depends, Query
from uuid import UUID, uuid4
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.starlette_injection import RequestHandler, MappingChain
from expert_dollup.app.dtos import ProjectDetailsDto, ProjectDetailsInputDto
from expert_dollup.core.domains import ProjectDetails
from expert_dollup.core.usecases import ProjectUseCase
from expert_dollup.app.jwt_auth import CanPerformOnRequired, CanPerformRequired

router = APIRouter()


@router.get("/project/{id}")
async def find_project_details(
    id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id, id, MappingChain(out_dto=ProjectDetailsDto)
    )


@router.post("/project")
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


@router.post("/project/{project_id}/clone")
async def clone_project(
    project_id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_id", ["project:read"], ["project:clone"])
    ),
):
    return await handler.forward(
        usecase.clone,
        dict(project_id=project_id, user=user),
        MappingChain(out_dto=ProjectDetailsDto),
    )


@router.delete("/project/{id}")
async def delete_project(
    id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
):
    await usecase.delete_by_id(id)

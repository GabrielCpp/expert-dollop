from fastapi import APIRouter, Depends, Query
from uuid import UUID, uuid4
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.app.dtos import ProjectDetailsDto, ProjectDetailsInputDto
from expert_dollup.core.domains import ProjectDetails
from expert_dollup.core.usecases import ProjectUseCase

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
):
    return await handler.handle(
        usecase.add,
        project,
        MappingChain(
            dto=ProjectDetailsInputDto, domain=ProjectDetails, out_dto=ProjectDetailsDto
        ),
    )


@router.post("/project/{project_id}/clone")
async def clone_project(
    project_id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.clone,
        project_id,
        MappingChain(out_dto=ProjectDetailsDto),
    )


@router.delete("/project/{id}")
async def delete_project(
    id: UUID,
    usecase=Depends(Inject(ProjectUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    await usecase.remove_by_id(id)

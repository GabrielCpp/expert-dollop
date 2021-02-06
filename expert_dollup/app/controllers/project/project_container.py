from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.usecases import ProjectContainerUseCase
from expert_dollup.core.domains import ProjectContainer
from expert_dollup.app.dtos import ProjectContainerDto, ProjectContainerTreeDto

router = APIRouter()


@router.get("/project/{project_id}/container/{container_id}")
async def get_project_container(
    project_id: UUID,
    container_id: UUID,
    usecase=Depends(Inject(ProjectContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id, container_id, MappingChain(out_dto=ProjectContainerDto)
    )


@router.get("/project/{project_id}/containers")
async def get_project_containers_by_path(
    project_id: UUID,
    path: List[UUID] = Query(alias="path", default=[]),
    level: Optional[int] = Query(alias="level", default=None),
    usecase=Depends(Inject(ProjectContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward(
        usecase.find_by_path,
        {"project_id": project_id, "path": path, "level": level},
        MappingChain(out_dto=ProjectContainerTreeDto),
    )


@router.put("/project/{project_id}/container/{container_id}/value")
async def add_project_container_collection(
    project_id: UUID,
    container_id: UUID,
    value: dict,
    usecase=Depends(Inject(ProjectContainerUseCase)),
):
    return await usecase.update_container_value(project_id, container_id, value)


@router.delete("/project/{id}/container")
async def remove_project_container(
    id: UUID, usecase=Depends(Inject(ProjectContainerUseCase))
):
    await usecase.remove(id)

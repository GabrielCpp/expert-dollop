from fastapi import APIRouter, Depends, Query
from typing import List
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.usecases import ProjectContainerUseCase
from expert_dollup.core.domains import ProjectContainer
from expert_dollup.app.dtos import ProjectContainerDto, ProjectContainerTreeDto

router = APIRouter()


@router.get("/project/{id}/container")
async def get_project_container(
    id: UUID,
    usecase=Depends(Inject(ProjectContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id, id, MappingChain(out_dto=ProjectContainerDto)
    )


@router.get("/project/{project_id}/containers")
async def get_project_containers_by_path(
    project_id: UUID,
    path: List[UUID] = Query(alias="path", default=[]),
    usecase=Depends(Inject(ProjectContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward(
        usecase.find_by_path,
        {"project_id": project_id, "path": path},
        MappingChain(out_dto=ProjectContainerTreeDto),
    )


@router.post("/project/{container_id}/container")
async def clone_project_container_collection(
    id: UUID, usecase=Depends(Inject(ProjectContainerUseCase))
):
    return await handler.handle(
        usecase.clone_collection,
        id,
        MappingChain(out_dto=ProjectContainerTreeDto),
    )


@router.post("/project/{container_id}/container")
async def add_project_container_collection(
    id: UUID, usecase=Depends(Inject(ProjectContainerUseCase))
):
    return await handler.handle(
        usecase.add_collection,
        id,
        MappingChain(out_dto=ProjectContainerTreeDto),
    )


@router.delete("/project/{id}/container")
async def remove_project_container(
    id: UUID, usecase=Depends(Inject(ProjectContainerUseCase))
):
    await usecase.remove(id)

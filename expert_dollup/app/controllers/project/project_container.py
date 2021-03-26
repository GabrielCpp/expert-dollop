from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.usecases import ProjectContainerUseCase
from expert_dollup.core.domains import (
    ProjectContainer,
    ProjectContainerFilter,
    ValueUnion,
)
from expert_dollup.app.dtos import (
    ProjectContainerDto,
    ProjectContainerTreeDto,
    ProjectContainerCollectionTargetDto,
    ProjectContainerPageDto,
    ValueUnionDto,
)

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
async def find_project_containers_by(
    project_id: UUID,
    type_id: UUID = Query(alias="typeId", default=None),
    usecase=Depends(Inject(ProjectContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward(
        usecase.find_by_type,
        {"project_id": project_id, "type_id": type_id},
        MappingChain(out_dto=ProjectContainerPageDto),
    )


@router.get("/project/{project_id}/children")
async def find_project_children_tree(
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


@router.get("/project/{project_id}/container/{container_id}/subtree")
async def find_project_container_subtree(
    project_id: UUID,
    container_id: UUID,
    usecase=Depends(Inject(ProjectContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward(
        usecase.find_subtree,
        {"project_id": project_id, "container_id": container_id},
        MappingChain(out_dto=ProjectContainerTreeDto),
    )


@router.put("/project/{project_id}/container/{container_id}/value")
async def mutate_project_field(
    project_id: UUID,
    container_id: UUID,
    value: ValueUnionDto,
    usecase=Depends(Inject(ProjectContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward_mapped(
        usecase.update_container_value,
        dict(project_id=project_id, container_id=container_id, value=value),
        MappingChain(out_dto=ProjectContainerTreeDto),
        map_keys=dict(value=MappingChain(dto=ValueUnionDto, domain=ValueUnion)),
    )


@router.post("/project/{project_id}/container/collection")
async def add_project_collection(
    project_id: UUID,
    collection_target: ProjectContainerCollectionTargetDto,
    usecase=Depends(Inject(ProjectContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward(
        usecase.add_collection,
        {"project_id": project_id, **collection_target.dict()},
        MappingChain(out_dto=ProjectContainerTreeDto),
    )


@router.post("/project/{project_id}/container/{collection_container_id}/clone")
async def clone_project_collection(
    project_id: UUID,
    collection_container_id: UUID,
    usecase=Depends(Inject(ProjectContainerUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward(
        usecase.clone_collection,
        {"project_id": project_id, "container_id": collection_container_id},
        MappingChain(out_dto=ProjectContainerTreeDto),
    )


@router.delete("/project/{project_id}/container/{container_id}")
async def remove_project_container_collection(
    project_id: UUID,
    container_id: UUID,
    usecase=Depends(Inject(ProjectContainerUseCase)),
):
    await usecase.remove_collection(project_id, container_id)

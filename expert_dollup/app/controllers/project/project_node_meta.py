from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import (
    Inject,
    RequestHandler,
    MappingChain,
    CanPerformOnRequired,
    CanPerformRequired,
    Inject,
)
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.get("/projects/{project_id}/node_meta/{type_id}")
async def get_project_node_meta(
    project_id: UUID,
    type_id: UUID,
    service=Depends(Inject(CollectionService[ProjectNodeMeta])),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("project_id", ["project:get"])),
):
    return await handler.handle(
        service.find_one_by,
        ProjectNodeMetaFilter(project_id=project_id, type_id=type_id),
        MappingChain(out_dto=ProjectNodeMetaDto),
    )


@router.get("/projects/{project_id}/node/{node_id}/meta")
async def get_project_node_meta_definition(
    project_id: UUID,
    node_id: UUID,
    meta_service=Depends(Inject(CollectionService[ProjectNodeMeta])),
    node_service=Depends(Inject(CollectionService[ProjectNode])),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("project_id", ["project:get"])),
):
    node = await node_service.find_one_by(
        ProjectNodeFilter(project_id=project_id, id=node_id)
    )

    return await handler.handle(
        meta_service.find_one_by,
        ProjectNodeMetaFilter(project_id=project_id, type_id=node.type_id),
        MappingChain(out_dto=ProjectNodeMetaDto),
    )

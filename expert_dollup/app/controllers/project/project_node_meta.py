from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.starlette_injection import RequestHandler, MappingChain
from expert_dollup.infra.services import ProjectNodeMetaService
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.get("/project/{project_id}/node_meta/{type_id}")
async def get_project_node_meta(
    project_id: UUID,
    type_id: UUID,
    service=Depends(Inject(ProjectNodeMetaService)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        service.find_one_by,
        ProjectNodeMetaFilter(project_id=project_id, type_id=type_id),
        MappingChain(out_dto=ProjectNodeMetaDto),
    )

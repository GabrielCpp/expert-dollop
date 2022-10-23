from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *
from expert_dollup.core.usecases import AggregationUseCase

router = APIRouter()


@router.get(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates"
)
async def get_collection_aggregates(
    project_definition_id: UUID,
    collection_id: UUID,
    usecase: AggregationUseCase = Depends(Inject(AggregationUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await handler.do_handle(
        usecase.get_aggregates,
        MappingChain(dto=List[AggregateDto]),
        project_definition_id=project_definition_id,
        collection_id=collection_id,
    )


@router.put(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates"
)
async def update_collection_aggregates(
    project_definition_id: UUID,
    collection_id: UUID,
    aggregates: List[AggregateDto],
    usecase: AggregationUseCase = Depends(Inject(AggregationUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.do_handle(
        usecase.replace_aggregates,
        MappingChain(
            dto=List[AggregateDto],
        ),
        project_definition_id=project_definition_id,
        collection_id=collection_id,
        aggregates=MappingChain(
            dto=AggregateDto,
            domain=Label,
            value=aggregates,
        ),
    )

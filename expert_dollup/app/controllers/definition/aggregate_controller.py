from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List
from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *
from expert_dollup.core.usecases import *

router = APIRouter()


@router.get(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates/{aggregate_id}"
)
async def get_collection_aggregate(
    project_definition_id: UUID,
    collection_id: UUID,
    aggregate_id: UUID,
    service: Repository[Aggregate] = Depends(Inject(Repository[Aggregate])),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await handler.do_handle(
        service.find_one_by,
        MappingChain(dto=AggregateDto),
        query_filter=AggregateFilter(
            id=aggregate_id,
            collection_id=collection_id,
            project_definition_id=project_definition_id,
        ),
    )


@router.post(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates"
)
async def create_collection_aggregate(
    project_definition_id: UUID,
    collection_id: UUID,
    new_aggregate: NewAggregateDto,
    usecase: AggregateUseCase = Depends(Inject(AggregateUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:create"])
    ),
):
    return await handler.do_handle(
        usecase.create,
        MappingChain(
            domain=Aggregate,
            dto=AggregateDto,
        ),
        project_definition_id=project_definition_id,
        collection_id=collection_id,
        new_aggregate=MappingChain(
            dto=NewAggregateDto,
            domain=NewAggregate,
            value=new_aggregate,
        ),
    )


@router.delete(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates/{aggregate_id}"
)
async def delete_collection_aggregate(
    project_definition_id: UUID,
    collection_id: UUID,
    aggregate_id: UUID,
    service: Repository[Aggregate] = Depends(Inject(Repository[Aggregate])),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:delete"])
    ),
):
    await service.delete_by(
        AggregateFilter(
            id=aggregate_id,
            collection_id=collection_id,
            project_definition_id=project_definition_id,
        )
    )

from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import List, Optional
from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *
from expert_dollup.core.services import *

router = APIRouter()


@router.get(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates"
)
async def find_paginated_aggregates(
    project_definition_id: UUID,
    collection_id: UUID,
    query: str = Query(alias="query", default=""),
    limit: int = Query(alias="limit", default=10),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    paginator: Paginator[Aggregate] = Depends(Inject(Paginator[Aggregate])),
    handler=Depends(Inject(PageHandlerProxy)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    query_filter = AggregateFilter(
        project_definition_id=project_definition_id,
        collection_id=collection_id,
    )

    query = query.strip()
    if query != "":
        query_filter.put("name", query)

    return await handler.use_paginator(paginator).handle(
        AggregateDto,
        query_filter,
        limit,
        next_page_token,
    )


@router.get(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates/{aggregate_id}"
)
async def get_aggregate(
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
async def add_aggregate(
    project_definition_id: UUID,
    collection_id: UUID,
    new_aggregate: NewAggregateDto,
    usecase: AggregateService = Depends(Inject(AggregateService)),
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


@router.put(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates/{aggregate_id}"
)
async def update_aggregate(
    project_definition_id: UUID,
    collection_id: UUID,
    aggregate_id: UUID,
    replacement: NewAggregateDto,
    usecase: AggregateService = Depends(Inject(AggregateService)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:create"])
    ),
):
    return await handler.do_handle(
        usecase.update,
        MappingChain(
            domain=Aggregate,
            dto=AggregateDto,
        ),
        project_definition_id=project_definition_id,
        collection_id=collection_id,
        aggregate_id=aggregate_id,
        replacement=MappingChain(
            dto=NewAggregateDto,
            domain=NewAggregate,
            value=replacement,
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

    return aggregate_id

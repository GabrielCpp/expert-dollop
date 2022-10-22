from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *
from expert_dollup.core.usecases import AggregationUseCase

router = APIRouter()


@router.get("/definitions/{project_definition_id}/collections/{collection_id}")
async def get_label_collection_by_id(
    project_definition_id: UUID,
    collection_id: UUID,
    usecase: AggregationUseCase = Depends(Inject(AggregationUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.do_handle(
        usecase.find,
        MappingChain(dto=AggregateCollectionDto),
        project_definition_id=project_definition_id,
        collection_id=collection_id,
    )


@router.post("/definitions/{project_definition_id}/collections")
async def add_aggregate_collection(
    project_definition_id: UUID,
    new_aggregate_collection: NewAggregateCollectionDto,
    usecase: AggregationUseCase = Depends(Inject(AggregationUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.do_handle(
        usecase.add,
        MappingChain(dto=AggregateCollectionDto),
        project_definition_id=project_definition_id,
        new_aggregate_collection=MappingChain(
            dto=NewAggregateCollectionDto,
            domain=NewAggregateCollection,
            value=new_aggregate_collection,
        ),
    )


@router.put("/definitions/{project_definition_id}/collections/{collection_id}")
async def update_aggregate_collection(
    project_definition_id: UUID,
    new_aggregate_collection: NewAggregateCollectionDto,
    usecase: AggregationUseCase = Depends(Inject(AggregationUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.do_handle(
        usecase.update,
        MappingChain(dto=AggregateCollectionDto),
        project_definition_id=project_definition_id,
        collection_id=collection_id,
        new_aggregate_collection=MappingChain(
            dto=NewAggregateCollectionDto,
            domain=AggregateCollection,
            value=new_aggregate_collection,
        ),
    )


@router.delete("/definitions/{project_definition_id}/collections/{collection_id}")
async def delete_aggregate_collection_by_id(
    project_definition_id: UUID,
    collection_id: UUID,
    usecase=Depends(Inject(AggregationUseCase)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    await usecase.delete(project_definition_id, collection_id)
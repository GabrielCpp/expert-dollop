from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *
from expert_dollup.core.usecases import LabelCollectionUseCase

router = APIRouter()


@router.get("/definitions/{project_definition_id}/collections/{collection_id}")
async def get_label_collection_by_id(
    project_definition_id: UUID,
    collection_id: UUID,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.handle(
        usecase.find_by_id,
        collection_id,
        MappingChain(out_dto=AggregateCollectionDto),
    )


@router.post("/definitions/{project_definition_id}/collections")
async def add_aggregate_collection(
    project_definition_id: UUID,
    new_aggregate_collection: NewAggregateCollectionDto,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.handle(
        usecase.add,
        new_aggregate_collection,
        MappingChain(
            dto=NewAggregateCollectionDto,
            domain=LabelCollection,
            out_dto=AggregateCollectionDto,
        ),
    )


@router.put("/definitions/{project_definition_id}/collections/{collection_id}")
async def update_aggregate_collection(
    project_definition_id: UUID,
    aggregate_collection: NewAggregateCollectionDto,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.handle(
        usecase.update,
        aggregate_collection,
        MappingChain(
            dto=NewAggregateCollectionDto,
            domain=LabelCollection,
            out_dto=AggregateCollectionDto,
        ),
    )


@router.delete("/definitions/{project_definition_id}/collections/{collection_id}")
async def delete_aggregate_collection_by_id(
    project_definition_id: UUID,
    collection_id: UUID,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await usecase.delete_by_id(collection_id)

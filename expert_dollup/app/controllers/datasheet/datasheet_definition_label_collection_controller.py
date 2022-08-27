from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *
from expert_dollup.core.usecases import LabelCollectionUseCase

router = APIRouter()


@router.get(
    "/definitions/{project_definition_id}/label_collections/{label_collection_id}"
)
async def get_label_collection_by_id(
    project_definition_id: UUID,
    label_collection_id: UUID,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.handle(
        usecase.find_by_id,
        label_collection_id,
        MappingChain(out_dto=LabelCollectionDto),
    )


@router.post("/definitions/{project_definition_id}/label_collections")
async def add_label_collection(
    project_definition_id: UUID,
    label_collection: LabelCollectionDto,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.handle(
        usecase.add,
        label_collection,
        MappingChain(
            dto=LabelCollectionDto,
            domain=LabelCollection,
            out_dto=LabelCollectionDto,
        ),
    )


@router.put("/definitions/{project_definition_id}/label_collections")
async def add_label_collection(
    project_definition_id: UUID,
    label_collection: LabelCollectionDto,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.handle(
        usecase.update,
        label_collection,
        MappingChain(
            dto=LabelCollectionDto,
            domain=LabelCollection,
            out_dto=LabelCollectionDto,
        ),
    )


@router.delete(
    "/definitions/{project_definition_id}/label_collections/{label_collection_id}"
)
async def delete_label_collection_by_id(
    project_definition_id: UUID,
    label_collection_id: UUID,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await usecase.delete_by_id(label_collection_id)

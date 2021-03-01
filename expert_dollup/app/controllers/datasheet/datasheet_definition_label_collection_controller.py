from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.domains import LabelCollection
from expert_dollup.app.dtos import LabelCollectionDto
from expert_dollup.core.usecases import LabelCollectionUseCase

router = APIRouter()


@router.get("/label_collection/{label_collection_id}")
async def get_label_collection_by_id(
    label_collection_id: UUID,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id,
        label_collection_id,
        MappingChain(out_dto=LabelCollectionDto),
    )


@router.post("/label_collection")
async def add_label_collection(
    label_collection: LabelCollectionDto,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
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


@router.put("/label_collection")
async def add_label_collection(
    label_collection: LabelCollectionDto,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
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


@router.delete("/label_collection/{label_collection_id}")
async def delete_label_collection_by_id(
    label_collection_id: UUID,
    usecase=Depends(Inject(LabelCollectionUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await usecase.delete_by_id(label_collection_id)

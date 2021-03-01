from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.domains import Label
from expert_dollup.app.dtos import LabelDto
from expert_dollup.core.usecases import LabelUseCase

router = APIRouter()


@router.get("/label/{label_id}")
async def get_label_by_id(
    label_id: UUID,
    usecase=Depends(Inject(LabelUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id,
        label_id,
        MappingChain(out_dto=LabelDto),
    )


@router.post("/label")
async def add_label(
    label: LabelDto,
    usecase=Depends(Inject(LabelUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.add,
        label,
        MappingChain(
            dto=LabelDto,
            domain=Label,
            out_dto=LabelDto,
        ),
    )


@router.put("/label")
async def add_label(
    label: LabelDto,
    usecase=Depends(Inject(LabelUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.update,
        label,
        MappingChain(
            dto=LabelDto,
            domain=Label,
            out_dto=LabelDto,
        ),
    )


@router.delete("/label/{label_id}")
async def delete_label_by_id(
    label_id: UUID,
    usecase=Depends(Inject(LabelUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await usecase.delete_by_id(label_id)

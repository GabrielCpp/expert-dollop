from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional, Union, Dict
from expert_dollup.shared.database_services import Page
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.domains import (
    Datasheet,
    DatasheetElement,
    PaginatedRessource,
    DatasheetElementId,
    DatasheetCloneTarget,
    DatasheetFilter,
)
from expert_dollup.app.dtos import (
    NewDatasheetDto,
    DatasheetDto,
    DatasheetElementDto,
    DatasheetElementPageDto,
    DatasheetCloneTargetDto,
    DatasheetUpdateDto,
)
from expert_dollup.core.usecases import DatasheetUseCase

router = APIRouter()


@router.get("/datasheet/{datasheet_id}")
async def find_datasheet_by_id(
    datasheet_id: UUID,
    usecase=Depends(Inject(DatasheetUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id,
        datasheet_id,
        MappingChain(
            domain=Datasheet,
            out_dto=DatasheetDto,
        ),
    )


@router.post("/datasheet")
async def add_datasheet(
    datasheet: NewDatasheetDto,
    usecase=Depends(Inject(DatasheetUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.add,
        datasheet,
        MappingChain(
            dto=NewDatasheetDto,
            domain=Datasheet,
            out_dto=DatasheetDto,
        ),
    )


@router.patch("/datasheet")
async def patch_datasheet(
    datasheet_update: DatasheetUpdateDto,
    usecase=Depends(Inject(DatasheetUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward(
        usecase.update,
        dict(
            datasheet_id=datasheet_update.id,
            updates=DatasheetFilter(
                **dict(
                    (k, v)
                    for k, v in datasheet_update.updates.dict().items()
                    if v is not None
                )
            ),
        ),
        MappingChain(out_dto=DatasheetDto),
    )


@router.post("/datasheet/clone")
async def clone_datsheet(
    datasheet_target: DatasheetCloneTargetDto,
    usecase=Depends(Inject(DatasheetUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.clone,
        datasheet_target,
        MappingChain(
            dto=DatasheetCloneTargetDto,
            domain=DatasheetCloneTarget,
            out_dto=DatasheetDto,
        ),
    )


@router.delete("/datasheet/{datasheet_id}")
async def delete_datsheet(
    datasheet_id: UUID,
    usecase=Depends(Inject(DatasheetUseCase)),
):
    await usecase.delete_by_id(datasheet_id)
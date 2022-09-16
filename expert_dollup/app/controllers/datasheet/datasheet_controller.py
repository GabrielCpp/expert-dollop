from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional, Union, Dict
from expert_dollup.shared.database_services import *
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.usecases import *
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *


router = APIRouter()


@router.get("/datasheets")
async def find_paginated_datasheets(
    query: str = Query(alias="query", default=""),
    limit: int = Query(alias="limit", default=10),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    paginator=Depends(Inject(UserRessourcePaginator[Datasheet])),
    handler: PageHandlerProxy = Depends(Inject(PageHandlerProxy)),
    user=Depends(CanPerformRequired(["datasheet:get"])),
):
    return await handler.use_paginator(paginator).handle(
        DatasheetDto,
        UserRessourceQuery(organization_id=user.organization_id, names=query.split()),
        limit,
        next_page_token,
    )


@router.get("/datasheets/{datasheet_id}")
async def find_datasheet_by_id(
    datasheet_id: UUID,
    usecase=Depends(Inject(DatasheetUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends((CanPerformOnRequired("datasheet_id", ["datasheet:get"]))),
):
    return await handler.handle(
        usecase.find_by_id,
        datasheet_id,
        MappingChain(
            domain=Datasheet,
            out_dto=DatasheetDto,
        ),
    )


@router.post("/datasheets")
async def add_datasheet(
    datasheet: NewDatasheetDto,
    usecase=Depends(Inject(DatasheetUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformRequired(["datasheet:create"])),
):
    return await handler.forward_mapped(
        usecase.add_filled_datasheet,
        dict(datasheet=datasheet, user=user),
        MappingChain(out_dto=DatasheetDto),
        {
            "datasheet": MappingChain(
                dto=NewDatasheetDto,
                domain=Datasheet,
            ),
        },
    )


@router.patch("/datasheets/{datasheet_id}")
async def patch_datasheet(
    datasheet_id: UUID,
    datasheet_update: DatasheetUpdateDto,
    usecase=Depends(Inject(DatasheetUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:update"])),
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


@router.post("/datasheets/{target_datasheet_id}/clone")
async def clone_datasheet(
    datasheet_target: DatasheetCloneTargetDto,
    usecase=Depends(Inject(DatasheetUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired(
            "target_datasheet_id", ["datasheet:get"], ["datasheet:clone"]
        )
    ),
):
    return await handler.forward_mapped(
        usecase.clone,
        dict(datasheet_clone_target=datasheet_target, user=user),
        MappingChain(out_dto=DatasheetDto),
        {
            "datasheet_clone_target": MappingChain(
                dto=DatasheetCloneTargetDto,
                domain=DatasheetCloneTarget,
            ),
        },
    )


@router.delete("/datasheets/{datasheet_id}")
async def delete_datasheet(
    datasheet_id: UUID,
    usecase=Depends(Inject(DatasheetUseCase)),
    user=Depends(CanPerformOnRequired("datasheet_id", ["datasheet:delete"])),
):
    await usecase.delete_by_id(datasheet_id)

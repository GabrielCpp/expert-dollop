from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    Inject,
    MappingChain,
)

router = APIRouter()


@router.get("/units")
async def get_measure_units(
    service=Depends(Inject(CollectionService[MeasureUnit])),
    handler=Depends(Inject(RequestHandler)),
) -> List[MeasureUnitDto]:
    return await handler.forward_many(
        service.find_all,
        dict(),
        MappingChain(domain=MeasureUnit, out_dto=MeasureUnitDto),
    )

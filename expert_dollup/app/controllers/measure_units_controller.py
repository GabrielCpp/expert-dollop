from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services import Repository
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    Inject,
    MappingChain,
)

router = APIRouter()


@router.get("/units")
async def get_measure_units(
    service=Depends(Inject(Repository[MeasureUnit])),
    handler=Depends(Inject(RequestHandler)),
) -> List[MeasureUnitDto]:
    return await handler.forward_many(
        service.all,
        dict(),
        MappingChain(domain=MeasureUnit, out_dto=MeasureUnitDto),
    )

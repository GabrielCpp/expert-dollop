from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import *
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *
from expert_dollup.core.usecases import LabelUseCase

router = APIRouter()


@router.get(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates"
)
async def get_label_by_id(
    project_definition_id: UUID,
    label_id: UUID,
    usecase=Depends(Inject(LabelUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await handler.handle(
        usecase.find_by_id,
        label_id,
        MappingChain(out_dto=LabelDto),
    )


@router.put(
    "/definitions/{project_definition_id}/collections/{collection_id}/aggregates"
)
async def add_label(
    project_definition_id: UUID,
    label: LabelDto,
    usecase=Depends(Inject(LabelUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
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

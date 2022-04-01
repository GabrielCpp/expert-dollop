from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *
from expert_dollup.core.usecases import DistributableUseCase
from expert_dollup.shared.starlette_injection import (
    RequestHandler,
    MappingChain,
    Inject,
)


router = APIRouter()


@router.get("/projects/{project_id}/distributables")
async def get_project_distributables(
    project_id: UUID,
    usecase=Depends(Inject(DistributableUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle_many(
        usecase.distributable_reports,
        project_id,
        MappingChain(domain=ReportDefinition, out_dto=ReportDefinitionDto),
    )


@router.put("/projects/{project_id}/distributable/{report_definition_id}")
async def get_project_distributable(
    project_id: UUID,
    report_definition_id: UUID,
    usecase=Depends(Inject(DistributableUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward(
        usecase.update_distributable,
        dict(project_id=project_id, report_definition_id=report_definition_id),
        MappingChain(domain=Distributable, out_dto=DistributableDto),
    )


@router.post("/projects/{project_id}/distributable/{report_definition_id}")
async def distribute_items(
    project_id: UUID,
    report_definition_id: UUID,
    items: List[UUID],
    usecase=Depends(Inject(DistributableUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.distribute(
        usecase.distribute,
        dict(
            project_id=project_id,
            report_definition_id=report_definition_id,
            items=items,
        ),
        MappingChain(domain=Distributable, out_dto=DistributableDto),
    )

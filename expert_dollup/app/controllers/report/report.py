from fastapi import APIRouter, Depends
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.starlette_injection import RequestHandler, MappingChain
from expert_dollup.core.usecases import ReportUseCase
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.get("/project/{project_id}/reports")
async def get_avaible_reports(
    project_id: UUID,
    usecase=Depends(Inject(ReportUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.forward_many(
        usecase.get_avaible_reports,
        dict(project_id=project_id),
        MappingChain(
            domain=ReportRow,
            out_dto=ReportDefinitionDto,
        ),
    )


@router.get("/project/{project_id}/report/{report_definition_id}")
async def get_project_report(
    project_id: UUID,
    report_definition_id: UUID,
    usecase=Depends(Inject(ReportUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    results = await handler.forward_many(
        usecase.get_report_rows,
        dict(project_id=project_id, report_definition_id=report_definition_id),
        MappingChain(
            domain=ReportRow,
            out_dto=ReportLightRowDto,
        ),
    )

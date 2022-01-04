from fastapi import APIRouter, Depends
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.starlette_injection import RequestHandler, MappingChain
from expert_dollup.core.usecases import ReportUseCase
from expert_dollup.core.domains import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.get("/project/{project_id}/report/{report_definition_id}")
async def get_project_report(
    project_id: UUID,
    report_definition_id: UUID,
    usecase: ReportUseCase = Depends(Inject(ReportUseCase)),
    handler=Depends(Inject(RequestHandler)),
):

    return await handler.forward(
        usecase.get_report,
        dict(project_id=project_id, report_definition_id=report_definition_id),
        MappingChain(
            domain=Report,
            out_dto=ReportDto,
        ),
    )

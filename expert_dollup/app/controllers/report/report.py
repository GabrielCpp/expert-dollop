from fastapi import APIRouter, Depends
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.starlette_injection import RequestHandler, MappingChain

router = APIRouter()


@router.get("/project/{project_id}/report/{report_definition_id}")
def get_project_report(
    project_id: UUID,
    report_definition_id: UUID,
    usecase=Depends(Inject(ReportUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    pass
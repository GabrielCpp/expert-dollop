from fastapi import APIRouter, Depends
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.starlette_injection import RequestHandler, MappingChain
from expert_dollup.core.usecases import ReportDefinitionUseCase

router = APIRouter()


@router.post("/report_definition/{report_definition_id}/refresh_cache")
def refresh_Report_definition_rows_cache(
    report_definition_id: UUID,
    usecase=Depends(Inject(ReportDefinitionUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    pass
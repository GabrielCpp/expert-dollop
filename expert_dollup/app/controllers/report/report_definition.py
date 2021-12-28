from fastapi import APIRouter, Depends
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.core.usecases import ReportDefinitionUseCase

router = APIRouter()


@router.post("/report_definition/{report_definition_id}/refresh_cache")
async def refresh_report_definition_rows_cache(
    report_definition_id: UUID,
    usecase=Depends(Inject(ReportDefinitionUseCase)),
):
    await usecase.refresh_cache(report_definition_id)

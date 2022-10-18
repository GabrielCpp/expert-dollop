from uuid import UUID
from fastapi import APIRouter, Depends
from expert_dollup.shared.starlette_injection import (
    Inject,
    RequestHandler,
    MappingChain,
)
from expert_dollup.shared.database_services import Repository
from expert_dollup.core.usecases import ReportDefinitionUseCase
from expert_dollup.core.domains import ReportDefinition
from expert_dollup.app.dtos import ReportDefinitionDto

router = APIRouter()


@router.post(
    "/definitions/{project_definition_id}/reports/{report_definition_id}/refresh_cache"
)
async def refresh_report_definition_rows_cache(
    report_definition_id: UUID,
    usecase=Depends(Inject(ReportDefinitionUseCase)),
):
    await usecase.refresh_cache(report_definition_id)


@router.post("/definitions/{project_definition_id}/reports/{report_definition_id}")
async def get_report_definition(
    report_definition_id: UUID,
    service: Repository[ReportDefinition] = Depends(
        Inject(Repository[ReportDefinition])
    ),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        service.find_by_id,
        report_definition_id,
        MappingChain(
            domain=ReportDefinition,
            out_dto=ReportDefinitionDto,
        ),
    )


@router.post("/definitions/{project_definition_id}/report_definitions")
async def get_project_def_reports_definitions(
    project_definition_id: UUID,
    usecase: ReportDefinitionUseCase = Depends(Inject(ReportDefinitionUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle_many(
        usecase.find_all_reports_definitions,
        project_definition_id,
        MappingChain(
            domain=ReportDefinition,
            out_dto=ReportDefinitionDto,
        ),
    )

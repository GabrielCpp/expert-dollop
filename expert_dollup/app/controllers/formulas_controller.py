from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional
from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.core.domains import *
from expert_dollup.core.usecases import *
from expert_dollup.app.dtos import *

router = APIRouter()


@router.get("/definitions/{project_definition_id}/formulas")
async def find_paginated_formulas(
    project_definition_id: UUID,
    limit: int = Query(alias="limit", default=10),
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    handler=Depends(Inject(PageHandlerProxy)),
    paginator=Depends(Inject(Paginator[FormulaExpression])),
):
    return await handler.use_paginator(paginator).handle(
        FormulaExpressionDto,
        FormulaFilter(project_definition_id=project_definition_id),
        limit,
        next_page_token,
    )


@router.get("/formula/{formula_id}")
async def get_formula(
    formula_id: UUID,
    usecase=Depends(Inject(FormulaUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id,
        formula_id,
        MappingChain(out_dto=FormulaExpressionDto),
    )


@router.get("/formula/{formula_id}")
async def get_formula(
    formula_id: UUID,
    usecase=Depends(Inject(FormulaUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id,
        formula_id,
        MappingChain(out_dto=FormulaExpressionDto),
    )


@router.post("/formula")
async def add_formula(
    formula: InputFormulaDto,
    usecase: FormulaUseCase = Depends(Inject(FormulaUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.add,
        formula,
        MappingChain(
            dto=InputFormulaDto, domain=FormulaExpression, out_dto=FormulaExpressionDto
        ),
    )


@router.delete("/formula/{formula_id}")
async def remove_formula(
    formula_id: UUID,
    remove_recursively: bool = Query(alias="removeRecursively", default=False),
    usecase=Depends(Inject(FormulaUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await usecase.delete_by_id(formula_id, remove_recursively)


@router.post("/projects/{project_id}/formula_cache")
async def refresh_formula_cache(
    project_id: UUID,
    usecase=Depends(Inject(FormulaUseCase)),
):
    await usecase.compute_project_formulas(project_id)

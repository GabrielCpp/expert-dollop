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
    paginator=Depends(Inject(Paginator[Formula])),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await handler.use_paginator(paginator).handle(
        FormulaExpressionDto,
        FormulaFilter(project_definition_id=project_definition_id),
        limit,
        next_page_token,
    )


@router.get("/definitions/{project_definition_id}/formulas/{formula_id}")
async def find_formula_by_id(
    project_definition_id: UUID,
    formula_id: UUID,
    usecase=Depends(Inject(FormulaUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:get"])
    ),
):
    return await handler.handle(
        usecase.find,
        formula_id,
        MappingChain(out_dto=FormulaExpressionDto),
    )


@router.post("/definitions/{project_definition_id}/formulas")
async def add_formula(
    project_definition_id: UUID,
    formula: InputFormulaDto,
    usecase: FormulaUseCase = Depends(Inject(FormulaUseCase)),
    handler: RequestHandler = Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:update"])
    ),
):
    return await handler.handle(
        usecase.add,
        formula,
        MappingChain(
            dto=InputFormulaDto, domain=FormulaExpression, out_dto=FormulaExpressionDto
        ),
    )


@router.delete("/definitions/{project_definition_id}/formulas/{formula_id}")
async def remove_formula(
    project_definition_id: UUID,
    formula_id: UUID,
    remove_recursively: bool = Query(alias="removeRecursively", default=False),
    usecase=Depends(Inject(FormulaUseCase)),
    handler=Depends(Inject(RequestHandler)),
    user=Depends(
        CanPerformOnRequired("project_definition_id", ["project_definition:delete"])
    ),
):
    return await usecase.delete(formula_id, remove_recursively)

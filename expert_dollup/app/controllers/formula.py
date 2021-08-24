from fastapi import APIRouter, Depends, Query
from uuid import UUID
from typing import Optional
from expert_dollup.shared.handlers import HttpPageHandler
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.domains import Formula, FormulaFilter
from expert_dollup.app.dtos import FormulaDto, InputFormulaDto
from expert_dollup.core.usecases import FormulaUseCase
from expert_dollup.infra.services import FormulaService

router = APIRouter()


@router.get("/project_definition/{project_def_id}/formulas")
async def get_formulas(
    project_def_id: UUID,
    limit: int = 10,
    next_page_token: Optional[str] = Query(alias="nextPageToken", default=None),
    handler=Depends(Inject(HttpPageHandler[FormulaService, FormulaDto])),
):
    return await handler.handle(
        FormulaFilter(project_def_id=project_def_id), limit, next_page_token
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
        MappingChain(out_dto=FormulaDto),
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
        MappingChain(out_dto=FormulaDto),
    )


@router.post("/formula")
async def add_formula(
    formula: InputFormulaDto,
    usecase=Depends(Inject(FormulaUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.add,
        formula,
        MappingChain(dto=InputFormulaDto, domain=Formula, out_dto=FormulaDto),
    )


@router.delete("/formula/{formula_id}")
async def remove_formula(
    formula_id: UUID,
    remove_recursively: bool = Query(alias="removeRecursively", default=False),
    usecase=Depends(Inject(FormulaUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await usecase.remove_by_id(formula_id, remove_recursively)


@router.post("/project/{project_id}/formula_cache")
async def add_formula(
    project_id: UUID,
    usecase=Depends(Inject(FormulaUseCase)),
):
    await usecase.compute_project_formulas(project_id)

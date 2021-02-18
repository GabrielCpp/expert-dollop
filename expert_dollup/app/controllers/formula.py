from fastapi import APIRouter, Depends, Query
from uuid import UUID
from expert_dollup.shared.starlette_injection import Inject
from expert_dollup.shared.handlers import RequestHandler, MappingChain
from expert_dollup.core.domains import Formula
from expert_dollup.app.dtos import FormulaDto
from expert_dollup.core.usecases import FormulaUseCase

router = APIRouter()


@router.get("/formula/{formula_id}")
async def get_formula(
    formula_id: UUID,
    usecase=Depends(Inject(FormulaUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.find_by_id,
        formula_id,
        MappingChain(out_dto=Formula),
    )


@router.post("/formula")
async def add_formula(
    formula: FormulaDto,
    usecase=Depends(Inject(FormulaUseCase)),
    handler=Depends(Inject(RequestHandler)),
):
    return await handler.handle(
        usecase.add,
        formula,
        MappingChain(dto=FormulaDto, domain=Formula, out_dto=FormulaDto),
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
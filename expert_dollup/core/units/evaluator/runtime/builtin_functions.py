from decimal import Decimal
from typing import Protocol, Any, Dict, List
from .flat_ast_evaluator import Computation, ComputationContext, AnyCallable


def safe_div(scope: ComputationContext, args: List[Computation]) -> Decimal:
    a = args[0].value
    b = args[1].value
    assert isinstance(a, Decimal), f"{type(a)} -> {a}"
    assert isinstance(b, Decimal), f"{type(b)} -> {b}"

    if b.is_zero():
        return Decimal(0)

    return a / b


def multi_type_sqrt(scope: ComputationContext, args: list):
    a = args[0].value
    result = a.sqrt()
    return result


BUILD_INS: Dict[str, AnyCallable] = {"safe_div": safe_div, "sqrt": multi_type_sqrt}
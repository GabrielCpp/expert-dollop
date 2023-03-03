import pytest
from abc import ABC, abstractmethod
from tests.fixtures.mock_interface_utils import StrictInterfaceSetup
from tests.units.core.units.evaluator.fixtures import *


def test_evaluate_simple_ast_with_simple_operands():
    evaluator = FlatAstEvaluator()
    fixture = SimpleExpressionWithSimpleOperandFactory()

    result, details = evaluator.compute(fixture.flat_ast.dict(), fixture.lexical_scope)

    assert result == fixture.result


def test_evaluate_simple_ast_with_function_call():
    evaluator = FlatAstEvaluator(BUILD_INS)
    fixture = SimpleExpressionWithFunctionCall()

    result, details = evaluator.compute(fixture.flat_ast.dict(), fixture.lexical_scope)

    assert result == fixture.result


def test_evaluate_complex_ast_with_function_call_if_return():
    evaluator = FlatAstEvaluator()
    fixture = ComplexExpressionWithInnerFunction()

    result, details = evaluator.compute(fixture.flat_ast.dict(), fixture.lexical_scope)

    assert result == fixture.result


def test_evaluate_complex_ast_with_function_call():
    evaluator = FlatAstEvaluator()
    fixture = ComplexExpressionWithInnerFunction(
        lexical_scope=ReportLexicalScopeFactory(),
        result="floor_pmctp_10",
    )

    result, details = evaluator.compute(fixture.flat_ast.dict(), fixture.lexical_scope)

    assert result == fixture.result


def test_evaluate_complex_ast_with_function_call_elif_return():
    evaluator = FlatAstEvaluator()
    unit = Unit(
        node_id="dummy", path=["a", "b", "c"], name="pmccu_choice", value="pmchr"
    )
    injector = UnitInjector(unit)
    fixture = ComplexExpressionWithInnerFunction(
        lexical_scope=ReportLexicalScopeFactory(injector=Computation(value=injector)),
        result="floor_first_floor_2",
    )

    result, details = evaluator.compute(fixture.flat_ast.dict(), fixture.lexical_scope)

    assert result == fixture.result


class PartialFormulaInjector(ABC):
    @abstractmethod
    def get_one_value(self, node_id, path, name, default):
        pass


def test_evaluate_complex_ast_with_report_get_room_floor():
    evaluator = FlatAstEvaluator()
    partial_formula_injector = StrictInterfaceSetup(PartialFormulaInjector)
    fixture = ComplexExpressionWithReportingIfElseSwitch(
        lexical_scope={
            "row": Computation(
                {
                    "floor": {"name": "Gabriel"},
                    "formula": {"node_id": "123", "path": [1, 2, 3]},
                }
            ),
            "injector": Computation(partial_formula_injector.object),
        }
    )

    partial_formula_injector.setup(
        lambda x: x.get_one_value("123", [1, 2, 3], "pmccu_choice", "Gabriel"),
        returns="pmchd",
    )

    result, details = evaluator.compute(fixture.flat_ast.dict(), fixture.lexical_scope)

    assert result == fixture.result


def test_evaluate_complex_ast_with_sum_generator():
    evaluator = FlatAstEvaluator()
    fixture = ComplexExpressionWithSumGenerator()

    result, details = evaluator.compute(fixture.flat_ast.dict(), fixture.lexical_scope)

    assert result == fixture.result

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
    fixture = ComplexExpressionWithInnerFunction(
        lexical_scope=dict(
            row=Computation(
                value={
                    "floor": {"name": "abcd"},
                    "formula": {"node_id": "id", "path": ["a", "b"]},
                }
            )
        ),
        result="abcd",
    )

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


report_get_room_floor = """
def get_room_floor(floor_name):
    floor_choice = injector.get_one_value(row['formula']['node_id'], row['formula']['path'], "pmccu_choice", floor_name)

    # Basement
    if floor_choice == "pmchs":
        floor_choice = "floor_basement_1"
    # 1er étage
    elif floor_choice == "pmchr":
        floor_choice = "floor_first_floor_2"
    # 2ieme étage
    elif floor_choice == "pmchd":
        floor_choice = "floor_second_floor_3"
    # 3ieme étage
    elif floor_choice == "pmcht":
        floor_choice = "floor_third_floor_4"
    # Quatrième
    elif floor_choice == "pmciz":
        floor_choice = "floor_fourth_floor_11"
    # Cinquième
    elif floor_choice == "pmcrq":
        floor_choice = "floor_fifth_floor_12"
    # Sixième
    elif floor_choice == "pmcrs":
        floor_choice = "floor_sixth_floor_13"
    # Garage
    elif floor_choice == "pmchg":
        floor_choice = "floor_garage_6"

    return floor_choice

get_room_floor(row['floor']['name'])
"""


class PartialFormulaInjector(ABC):
    @abstractmethod
    def get_one_value(self, node_id, path, name, default):
        pass


def test_report_get_room_floor():
    evaluator = FlatAstEvaluator()
    partial_formula_injector = StrictInterfaceSetup(PartialFormulaInjector)
    row = {
        "floor": {"name": "Gabriel"},
        "formula": {"node_id": "123", "path": [1, 2, 3]},
    }

    partial_formula_injector.setup(
        lambda x: x.get_one_value("123", [1, 2, 3], "pmccu_choice", "Gabriel"),
        returns="pmchd",
    )

    result = evaluator.compute(
        report_get_room_floor,
        {"row": row, "injector": partial_formula_injector.object},
    )

    assert result == "floor_second_floor_3"


def test_expression_evaluator_simple_mul():
    evaluator = FlatAstEvaluator()

    result = evaluator.compute(
        "sum(value * factor for value in values) * cost",
        {
            "values": [Decimal(682)],
            "cost": Decimal("197.99"),
            "factor": Decimal("0.0005"),
            "sum": sum,
        },
    )

    assert result == Decimal("67.514590")

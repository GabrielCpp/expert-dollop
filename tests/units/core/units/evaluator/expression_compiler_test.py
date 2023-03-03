import pytest
from tests.units.core.units.evaluator.fixtures import *


def test_compile_simple_expression_with_simple_operands():
    compiler = ExpressionCompiler.create_simple()
    fixture = SimpleExpressionWithSimpleOperandFactory()

    actual = compiler.compile(fixture.expression)

    assert actual == fixture.flat_ast


def test_compile_simple_expression_with_function_call():
    compiler = ExpressionCompiler.create_simple()
    fixture = SimpleExpressionWithFunctionCall()

    actual = compiler.compile(fixture.expression)

    assert actual == fixture.flat_ast


def test_given_formula_expression_should_produce_correct_serialized_ast():
    compiler = ExpressionCompiler.create_simple()
    expression = "mdcfg*((sgcgm-sgcpm)/2)"

    flat_ast = compiler.compile(expression)

    assert flat_ast == FlatAst(
        nodes=[
            AstNode(
                kind="Name",
                values={"id": "mdcfg", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "sgcgm", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "sgcpm", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Sub"},
                properties={"left": 1, "right": 2},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(number=Decimal("2"), text=None, enabled=None)
                },
                properties={},
                children={},
            ),
            AstNode(
                kind="Call",
                values={"fn_name": "safe_div"},
                properties={},
                children={"args": [3, 4]},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Mult"},
                properties={"left": 0, "right": 5},
                children={},
            ),
            AstNode(kind="Expr", values={}, properties={"value": 6}, children={}),
            AstNode(kind="Module", values={}, properties={"body": 7}, children={}),
        ],
        root_index=8,
    )


def test_given_formula_expression_when_expression_contain_function_should_produce_correct_serialized_ast():
    compiler = ExpressionCompiler.create_simple()
    expression = "mdcfg*(sqrt(sgchm*sgchm+sgpyg*sgpyg)*2)"

    flat_ast = compiler.compile(expression)

    assert flat_ast == FlatAst(
        nodes=[
            AstNode(
                kind="Name",
                values={"id": "mdcfg", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "sgchm", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "sgchm", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Mult"},
                properties={"left": 1, "right": 2},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "sgpyg", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "sgpyg", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Mult"},
                properties={"left": 4, "right": 5},
                children={},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Add"},
                properties={"left": 3, "right": 6},
                children={},
            ),
            AstNode(
                kind="Call",
                values={"fn_name": "sqrt"},
                properties={},
                children={"args": [7]},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(number=Decimal("2"), text=None, enabled=None)
                },
                properties={},
                children={},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Mult"},
                properties={"left": 8, "right": 9},
                children={},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Mult"},
                properties={"left": 0, "right": 10},
                children={},
            ),
            AstNode(kind="Expr", values={}, properties={"value": 11}, children={}),
            AstNode(kind="Module", values={}, properties={"body": 12}, children={}),
        ],
        root_index=13,
    )


def test_compile_complex_expression_with_inner_function():
    compiler = ExpressionCompiler.create_complex()
    fixture = ComplexExpressionWithInnerFunction()

    actual = compiler.compile(fixture.expression)

    assert actual == fixture.flat_ast


def test_compile_complex_expression_with_report_get_room_flor():
    compiler = ExpressionCompiler.create_complex()
    fixture = ComplexExpressionWithReportingIfElseSwitch()

    actual = compiler.compile(fixture.expression)

    assert actual == fixture.flat_ast


def test_compile_complex_expression_with_sum_generator():
    compiler = ExpressionCompiler.create_complex()
    fixture = ComplexExpressionWithSumGenerator()

    actual = compiler.compile(fixture.expression)

    assert actual == fixture.flat_ast

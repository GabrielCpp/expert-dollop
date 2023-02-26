from factory import Factory, SubFactory, DictFactory
from dataclasses import dataclass
from textwrap import dedent
from decimal import Decimal
from math import sqrt
from expert_dollup.core.domains import PrimitiveWithNoneUnion
from expert_dollup.core.units.evaluator import *


@dataclass
class ExpressionFixture:
    expression: str
    lexical_scope: LexicalScope
    result: PrimitiveWithNoneUnion
    flat_ast: FlatAst


class FlatAstFactory(Factory):
    class Meta:
        model = FlatAst


class LexicalScopeFacotry(DictFactory):
    pass


class SimpleExpressionWithSimpleOperandFactory(Factory):
    class Meta:
        model = ExpressionFixture

    expression = "2*x-1"
    result = 3
    lexical_scope = SubFactory(LexicalScopeFacotry, x=Computation(value=2))
    flat_ast = SubFactory(
        FlatAstFactory,
        nodes=[
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(number=Decimal("2"), text=None, enabled=None)
                },
            ),
            AstNode(
                kind="Name",
                values={"id": "x", "ctx": "Load"},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Mult"},
                properties={"left": 0, "right": 1},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(number=Decimal("1"), text=None, enabled=None)
                },
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Sub"},
                properties={"left": 2, "right": 3},
            ),
            AstNode(kind="Expr", values={}, properties={"value": 4}),
            AstNode(kind="Module", values={}, properties={"body": 5}),
        ],
        root_index=6,
    )


class SimpleExpressionWithFunctionCall(Factory):
    class Meta:
        model = ExpressionFixture

    expression = "sqrt(x*x)*y"
    result = 1
    lexical_scope = SubFactory(
        LexicalScopeFacotry,
        x=Computation(value=Decimal("2")),
        y=Computation(value=Decimal("0.5")),
    )
    flat_ast = SubFactory(
        FlatAstFactory,
        nodes=[
            AstNode(
                kind="Name",
                values={"id": "x", "ctx": "Load"},
            ),
            AstNode(
                kind="Name",
                values={"id": "x", "ctx": "Load"},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Mult"},
                properties={"left": 0, "right": 1},
            ),
            AstNode(
                kind="Call",
                values={"fn_name": "sqrt"},
                children={"args": [2]},
            ),
            AstNode(
                kind="Name",
                values={"id": "y", "ctx": "Load"},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Mult"},
                properties={"left": 3, "right": 4},
            ),
            AstNode(kind="Expr", values={}, properties={"value": 5}),
            AstNode(kind="Module", values={}, properties={"body": 6}),
        ],
        root_index=7,
    )


class ReportLexicalScopeFactory(DictFactory):
    injector = Computation(value=UnitInjector())
    row = Computation(
        value={
            "floor": {"name": "floor_pmctp_10"},
            "formula": {"node_id": "test-id", "path": ["a", "b"]},
        }
    )


class ComplexExpressionWithInnerFunction(Factory):
    class Meta:
        model = ExpressionFixture

    expression = dedent(
        """
    def get_room_floor(floor_name):
        if floor_name != "floor_pmctp_10":
            return floor_name
        floor_choice = injector.get_one_value(row['formula']['node_id'], row['formula']['path'], "pmccu_choice", floor_name)
        # Basement
        if floor_choice == "pmchs":
            floor_choice = "floor_basement_1"
        # 1er étage
        elif floor_choice == "pmchr":
            floor_choice = "floor_first_floor_2"

        return floor_choice

    get_room_floor(row['floor']['name'])
    """
    )

    result = 1
    lexical_scope = SubFactory(
        LexicalScopeFacotry,
        row=Computation(
            value={
                "floor": {"name": "pmchr"},
                "formula": {"node_id": "id", "path": ["a", "b"]},
            }
        ),
    )
    flat_ast = SubFactory(
        FlatAstFactory,
        nodes=[
            AstNode(
                kind="Name",
                values={"id": "floor_name", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(
                        number=None, text="floor_pmctp_10", enabled=None
                    )
                },
                properties={},
                children={},
            ),
            AstNode(
                kind="Compare",
                values={"ops": "NotEq"},
                properties={"left": 0},
                children={"comparators": [1]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_name", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(kind="Return", values={}, properties={"value": 3}, children={}),
            AstNode(
                kind="If",
                values={},
                properties={"test": 2},
                children={"body": [4], "orelse": []},
            ),
            AstNode(
                kind="Name",
                values={"id": "injector", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Attribute",
                values={"attr": "get_one_value"},
                properties={"value": 6},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "row", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(number=None, text="formula", enabled=None)
                },
                properties={},
                children={},
            ),
            AstNode(
                kind="Subscript",
                values={},
                properties={"value": 8, "slice": 9},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(number=None, text="node_id", enabled=None)
                },
                properties={},
                children={},
            ),
            AstNode(
                kind="Subscript",
                values={},
                properties={"value": 10, "slice": 11},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "row", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(number=None, text="formula", enabled=None)
                },
                properties={},
                children={},
            ),
            AstNode(
                kind="Subscript",
                values={},
                properties={"value": 13, "slice": 14},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="path", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Subscript",
                values={},
                properties={"value": 15, "slice": 16},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(
                        number=None, text="pmccu_choice", enabled=None
                    )
                },
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_name", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Call",
                values={},
                properties={"fn": 7},
                children={"args": [12, 17, 18, 19]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Save"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Assign",
                values={},
                properties={"value": 20},
                children={"targets": [21]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="pmchs", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Compare",
                values={"ops": "Eq"},
                properties={"left": 23},
                children={"comparators": [24]},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(
                        number=None, text="floor_basement_1", enabled=None
                    )
                },
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Save"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Assign",
                values={},
                properties={"value": 26},
                children={"targets": [27]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="pmchr", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Compare",
                values={"ops": "Eq"},
                properties={"left": 29},
                children={"comparators": [30]},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(
                        number=None, text="floor_first_floor_2", enabled=None
                    )
                },
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Save"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Assign",
                values={},
                properties={"value": 32},
                children={"targets": [33]},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 31},
                children={"body": [34], "orelse": []},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 25},
                children={"body": [28], "orelse": [35]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(kind="Return", values={}, properties={"value": 37}, children={}),
            AstNode(
                kind="FunctionDef",
                values={
                    "name": "get_room_floor",
                    "args": FunctionParams(positional_names=["floor_name"]),
                },
                properties={},
                children={"body": [5, 22, 36, 38]},
            ),
            AstNode(
                kind="Name",
                values={"id": "get_room_floor", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "row", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="floor", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Subscript",
                values={},
                properties={"value": 41, "slice": 42},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="name", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Subscript",
                values={},
                properties={"value": 43, "slice": 44},
                children={},
            ),
            AstNode(
                kind="Call", values={}, properties={"fn": 40}, children={"args": [45]}
            ),
            AstNode(kind="Expr", values={}, properties={"value": 46}, children={}),
            AstNode(
                kind="Module", values={}, properties={}, children={"body": [39, 47]}
            ),
        ],
        root_index=48,
    )

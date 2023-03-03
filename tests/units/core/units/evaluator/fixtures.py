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

    result = "abcd"
    lexical_scope = SubFactory(
        LexicalScopeFacotry,
        row=Computation(
            value={
                "floor": {"name": "abcd"},
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


class ComplexExpressionWithReportingIfElseSwitch(Factory):
    class Meta:
        model = ExpressionFixture

    expression = dedent(
        """
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
    )

    result = "floor_second_floor_3"
    lexical_scope = SubFactory(
        LexicalScopeFacotry,
        row=Computation(
            value={
                "floor": {"name": "abcd"},
                "formula": {"node_id": "id", "path": ["a", "b"]},
            }
        ),
    )
    flat_ast = SubFactory(
        FlatAstFactory,
        nodes=[
            AstNode(
                kind="Name",
                values={"id": "injector", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Attribute",
                values={"attr": "get_one_value"},
                properties={"value": 0},
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
                properties={"value": 2, "slice": 3},
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
                properties={"value": 4, "slice": 5},
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
                properties={"value": 7, "slice": 8},
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
                properties={"value": 9, "slice": 10},
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
                properties={"fn": 1},
                children={"args": [6, 11, 12, 13]},
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
                properties={"value": 14},
                children={"targets": [15]},
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
                properties={"left": 17},
                children={"comparators": [18]},
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
                values={"value": AstNodeValue(number=None, text="pmchr", enabled=None)},
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
                values={"value": AstNodeValue(number=None, text="pmchd", enabled=None)},
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
                        number=None, text="floor_second_floor_3", enabled=None
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
                kind="Name",
                values={"id": "floor_choice", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="pmcht", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Compare",
                values={"ops": "Eq"},
                properties={"left": 35},
                children={"comparators": [36]},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(
                        number=None, text="floor_third_floor_4", enabled=None
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
                properties={"value": 38},
                children={"targets": [39]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="pmciz", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Compare",
                values={"ops": "Eq"},
                properties={"left": 41},
                children={"comparators": [42]},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(
                        number=None, text="floor_fourth_floor_11", enabled=None
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
                properties={"value": 44},
                children={"targets": [45]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="pmcrq", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Compare",
                values={"ops": "Eq"},
                properties={"left": 47},
                children={"comparators": [48]},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(
                        number=None, text="floor_fifth_floor_12", enabled=None
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
                properties={"value": 50},
                children={"targets": [51]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="pmcrs", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Compare",
                values={"ops": "Eq"},
                properties={"left": 53},
                children={"comparators": [54]},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(
                        number=None, text="floor_sixth_floor_13", enabled=None
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
                properties={"value": 56},
                children={"targets": [57]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Constant",
                values={"value": AstNodeValue(number=None, text="pmchg", enabled=None)},
                properties={},
                children={},
            ),
            AstNode(
                kind="Compare",
                values={"ops": "Eq"},
                properties={"left": 59},
                children={"comparators": [60]},
            ),
            AstNode(
                kind="Constant",
                values={
                    "value": AstNodeValue(
                        number=None, text="floor_garage_6", enabled=None
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
                properties={"value": 62},
                children={"targets": [63]},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 61},
                children={"body": [64], "orelse": []},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 55},
                children={"body": [58], "orelse": [65]},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 49},
                children={"body": [52], "orelse": [66]},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 43},
                children={"body": [46], "orelse": [67]},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 37},
                children={"body": [40], "orelse": [68]},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 31},
                children={"body": [34], "orelse": [69]},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 25},
                children={"body": [28], "orelse": [70]},
            ),
            AstNode(
                kind="If",
                values={},
                properties={"test": 19},
                children={"body": [22], "orelse": [71]},
            ),
            AstNode(
                kind="Name",
                values={"id": "floor_choice", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(kind="Return", values={}, properties={"value": 73}, children={}),
            AstNode(
                kind="FunctionDef",
                values={
                    "name": "get_room_floor",
                    "args": FunctionParams(positional_names=["floor_name"]),
                },
                properties={},
                children={"body": [16, 72, 74]},
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
                properties={"value": 77, "slice": 78},
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
                properties={"value": 79, "slice": 80},
                children={},
            ),
            AstNode(
                kind="Call", values={}, properties={"fn": 76}, children={"args": [81]}
            ),
            AstNode(kind="Expr", values={}, properties={"value": 82}, children={}),
            AstNode(
                kind="Module", values={}, properties={}, children={"body": [75, 83]}
            ),
        ],
        root_index=84,
    )


class ComplexExpressionWithSumGenerator(Factory):
    class Meta:
        model = ExpressionFixture

    expression = "sum(value * factor for value in values) * cost"
    result = Decimal("67.514590")
    lexical_scope = SubFactory(
        LexicalScopeFacotry,
        values=Computation([Decimal(682)]),
        cost=Computation(Decimal("197.99")),
        factor=Computation(Decimal("0.0005")),
        sum=Computation(sum),
    )
    flat_ast = SubFactory(
        FlatAstFactory,
        nodes=[
            AstNode(
                kind="Name",
                values={"id": "sum", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "value", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "factor", "ctx": "Load"},
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
                values={"id": "values", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="Name",
                values={"id": "value", "ctx": "Save"},
                properties={},
                children={},
            ),
            AstNode(
                kind="comprehension",
                values={
                    "is_async": AstNodeValue(
                        number=Decimal("0"), text=None, enabled=None
                    )
                },
                properties={"iter": 4, "target": 5},
                children={"ifs": []},
            ),
            AstNode(
                kind="GeneratorExp",
                values={},
                properties={"elt": 3},
                children={"generators": [6]},
            ),
            AstNode(
                kind="Call", values={}, properties={"fn": 0}, children={"args": [7]}
            ),
            AstNode(
                kind="Name",
                values={"id": "cost", "ctx": "Load"},
                properties={},
                children={},
            ),
            AstNode(
                kind="BinOp",
                values={"op": "Mult"},
                properties={"left": 8, "right": 9},
                children={},
            ),
            AstNode(kind="Expr", values={}, properties={"value": 10}, children={}),
            AstNode(kind="Module", values={}, properties={}, children={"body": [11]}),
        ],
        root_index=12,
    )

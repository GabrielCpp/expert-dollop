from decimal import Decimal
from expert_dollup.core.logits import serialize_post_processed_expression


def test_given_formula_expression_should_produce_correct_serialized_ast():
    expression = "mdcfg*((sgcgm-sgcpm)/2)"
    serialized = serialize_post_processed_expression(expression)

    assert serialized == {
        "nodes": [
            {
                "kind": "Name",
                "values": {"id": "mdcfg"},
                "properties": {},
                "children": {},
            },
            {
                "kind": "Name",
                "values": {"id": "sgcgm"},
                "properties": {},
                "children": {},
            },
            {
                "kind": "Name",
                "values": {"id": "sgcpm"},
                "properties": {},
                "children": {},
            },
            {
                "kind": "BinOp",
                "values": {"op": "Sub"},
                "properties": {"left": 1, "right": 2},
                "children": {},
            },
            {
                "kind": "Constant",
                "values": {
                    "value": {
                        "number": Decimal("2.000000"),
                        "text": None,
                        "enabled": None,
                    }
                },
                "properties": {},
                "children": {},
            },
            {
                "kind": "Call",
                "values": {"fn_name": "safe_div"},
                "properties": {},
                "children": {"args": [3, 4]},
            },
            {
                "kind": "BinOp",
                "values": {"op": "Mult"},
                "properties": {"left": 0, "right": 5},
                "children": {},
            },
            {"kind": "Expr", "values": {}, "properties": {"value": 6}, "children": {}},
            {"kind": "Module", "values": {}, "properties": {"body": 7}, "children": {}},
        ],
        "root_index": 8,
    }


def test_given_formula_expression_when_expression_contain_function_should_produce_correct_serialized_ast():
    expression = "mdcfg*(sqrt(sgchm*sgchm+sgpyg*sgpyg)*2)"
    serialized = serialize_post_processed_expression(expression)

    assert serialized == {
        "nodes": [
            {
                "kind": "Name",
                "values": {"id": "mdcfg"},
                "properties": {},
                "children": {},
            },
            {
                "kind": "Name",
                "values": {"id": "sgchm"},
                "properties": {},
                "children": {},
            },
            {
                "kind": "Name",
                "values": {"id": "sgchm"},
                "properties": {},
                "children": {},
            },
            {
                "kind": "BinOp",
                "values": {"op": "Mult"},
                "properties": {"left": 1, "right": 2},
                "children": {},
            },
            {
                "kind": "Name",
                "values": {"id": "sgpyg"},
                "properties": {},
                "children": {},
            },
            {
                "kind": "Name",
                "values": {"id": "sgpyg"},
                "properties": {},
                "children": {},
            },
            {
                "kind": "BinOp",
                "values": {"op": "Mult"},
                "properties": {"left": 4, "right": 5},
                "children": {},
            },
            {
                "kind": "BinOp",
                "values": {"op": "Add"},
                "properties": {"left": 3, "right": 6},
                "children": {},
            },
            {
                "kind": "Call",
                "values": {"fn_name": "sqrt"},
                "properties": {},
                "children": {"args": [7]},
            },
            {
                "kind": "Constant",
                "values": {
                    "value": {
                        "number": Decimal("2.000000"),
                        "text": None,
                        "enabled": None,
                    }
                },
                "properties": {},
                "children": {},
            },
            {
                "kind": "BinOp",
                "values": {"op": "Mult"},
                "properties": {"left": 8, "right": 9},
                "children": {},
            },
            {
                "kind": "BinOp",
                "values": {"op": "Mult"},
                "properties": {"left": 0, "right": 10},
                "children": {},
            },
            {"kind": "Expr", "values": {}, "properties": {"value": 11}, "children": {}},
            {
                "kind": "Module",
                "values": {},
                "properties": {"body": 12},
                "children": {},
            },
        ],
        "root_index": 13,
    }

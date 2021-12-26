from expert_dollup.core.logits import serialize_post_processed_expression


def test_given_formula_expression_should_produce_correct_serialized_ast():
    expression = "mdcfg*((sgcgm-sgcpm)/2)"
    serialized = serialize_post_processed_expression(expression)
    assert serialized == {
        "kind": "Module",
        "values": {},
        "properties": {
            "body": {
                "kind": "Expr",
                "values": {},
                "properties": {
                    "value": {
                        "kind": "BinOp",
                        "values": {"op": "Mult"},
                        "properties": {
                            "left": {
                                "kind": "Name",
                                "values": {"id": "mdcfg"},
                                "properties": {},
                                "children": {},
                            },
                            "right": {
                                "kind": "Call",
                                "values": {"fn_name": "safe_div"},
                                "properties": {},
                                "children": {
                                    "args": [
                                        {
                                            "kind": "BinOp",
                                            "values": {"op": "Sub"},
                                            "properties": {
                                                "left": {
                                                    "kind": "Name",
                                                    "values": {"id": "sgcgm"},
                                                    "properties": {},
                                                    "children": {},
                                                },
                                                "right": {
                                                    "kind": "Name",
                                                    "values": {"id": "sgcpm"},
                                                    "properties": {},
                                                    "children": {},
                                                },
                                            },
                                            "children": {},
                                        },
                                        {
                                            "kind": "Constant",
                                            "values": {"value": 2},
                                            "properties": {},
                                            "children": {},
                                        },
                                    ]
                                },
                            },
                        },
                        "children": {},
                    }
                },
                "children": {},
            }
        },
        "children": {},
    }


def test_given_formula_expression_when_expression_contain_function_should_produce_correct_serialized_ast():
    expression = "mdcfg*(sqrt(sgchm*sgchm+sgpyg*sgpyg)*2)"
    serialized = serialize_post_processed_expression(expression)
    assert serialized == {
        "kind": "Module",
        "values": {},
        "properties": {
            "body": {
                "kind": "Expr",
                "values": {},
                "properties": {
                    "value": {
                        "kind": "BinOp",
                        "values": {"op": "Mult"},
                        "properties": {
                            "left": {
                                "kind": "Name",
                                "values": {"id": "mdcfg"},
                                "properties": {},
                                "children": {},
                            },
                            "right": {
                                "kind": "BinOp",
                                "values": {"op": "Mult"},
                                "properties": {
                                    "left": {
                                        "kind": "Call",
                                        "values": {"fn_name": "sqrt"},
                                        "properties": {},
                                        "children": {
                                            "args": [
                                                {
                                                    "kind": "BinOp",
                                                    "values": {"op": "Add"},
                                                    "properties": {
                                                        "left": {
                                                            "kind": "BinOp",
                                                            "values": {"op": "Mult"},
                                                            "properties": {
                                                                "left": {
                                                                    "kind": "Name",
                                                                    "values": {
                                                                        "id": "sgchm"
                                                                    },
                                                                    "properties": {},
                                                                    "children": {},
                                                                },
                                                                "right": {
                                                                    "kind": "Name",
                                                                    "values": {
                                                                        "id": "sgchm"
                                                                    },
                                                                    "properties": {},
                                                                    "children": {},
                                                                },
                                                            },
                                                            "children": {},
                                                        },
                                                        "right": {
                                                            "kind": "BinOp",
                                                            "values": {"op": "Mult"},
                                                            "properties": {
                                                                "left": {
                                                                    "kind": "Name",
                                                                    "values": {
                                                                        "id": "sgpyg"
                                                                    },
                                                                    "properties": {},
                                                                    "children": {},
                                                                },
                                                                "right": {
                                                                    "kind": "Name",
                                                                    "values": {
                                                                        "id": "sgpyg"
                                                                    },
                                                                    "properties": {},
                                                                    "children": {},
                                                                },
                                                            },
                                                            "children": {},
                                                        },
                                                    },
                                                    "children": {},
                                                }
                                            ]
                                        },
                                    },
                                    "right": {
                                        "kind": "Constant",
                                        "values": {"value": 2},
                                        "properties": {},
                                        "children": {},
                                    },
                                },
                                "children": {},
                            },
                        },
                        "children": {},
                    }
                },
                "children": {},
            }
        },
        "children": {},
    }

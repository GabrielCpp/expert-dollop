import ast
from uuid import UUID
from decimal import Decimal
from dataclasses import dataclass
from typing import Callable, Dict, Union, List, Any, Tuple, Type
from ..models import AstNode, AstNodeValue, FlatAst, FunctionParams

Serialize = Callable[["AstSerializer", Any], AstNode]
TypeSerializerMap = Dict[Type, Serialize]


class AstSerializer:
    def __init__(self, serializers: TypeSerializerMap):
        self.nodes = []
        self.serializers = serializers

    def serialize(self, node: ast.AST) -> int:
        node_type = type(node)

        if not node_type in self.serializers:
            raise Exception(f"Unsupported node {type(node)}: {node}")

        serialie = self.serializers[node_type]
        index = self._add(serialie(self, node))
        return index

    def flatify(self, node: ast.AST) -> FlatAst:
        root_index = self.serialize(node)
        return FlatAst(nodes=self.nodes, root_index=root_index)

    def _add(self, node: AstNode) -> int:
        index = len(self.nodes)
        self.nodes.append(node)
        return index


def make_number(value: Union[None, str, bytes, bool, int, float, complex, Decimal]):
    casted_value: Union[str, bool, int, float, Decimal] = 0

    if isinstance(value, bytes):
        casted_value = value.decode("utf8")
    elif isinstance(value, complex):
        casted_value = value.real
    elif not value is None:
        casted_value = value

    return AstNodeValue(number=Decimal(casted_value))


def make_value(
    value: Union[None, str, bytes, bool, int, float, complex, Decimal]
) -> AstNodeValue:
    casted_value: Union[str, bool, int, float, Decimal] = 0

    if isinstance(value, bytes):
        casted_value = value.decode("utf8")
    elif isinstance(value, complex):
        casted_value = value.real
    elif not value is None:
        casted_value = value

    if isinstance(casted_value, (float, int)):
        return make_number(casted_value)

    if isinstance(casted_value, str):
        return AstNodeValue(text=casted_value)

    if isinstance(casted_value, Decimal):
        return AstNodeValue(number=casted_value)

    raise Exception(f"Unsupported type {type(casted_value)} with value {casted_value}")


def add_known_ctx(values: Dict[str, str], ctx: ast.expr_context):
    if isinstance(ctx, ast.Load):
        values["ctx"] = "Load"

    if isinstance(ctx, ast.Store):
        values["ctx"] = "Save"


def add_trivial_module(s: AstSerializer, node: ast.Module) -> AstNode:
    if len(node.body) > 1:
        raise Exception("Body of simple expression can only have one element")

    return AstNode(kind="Module", properties={"body": s.serialize(node.body[0])})


def add_module(s: AstSerializer, node: ast.Module) -> AstNode:
    return AstNode(
        kind="Module",
        children={"body": [s.serialize(element) for element in node.body]},
    )


def add_expr(s: AstSerializer, node: ast.Expr) -> AstNode:
    return AstNode(kind="Expr", properties={"value": s.serialize(node.value)})


def add_name(s: AstSerializer, node: ast.Name) -> AstNode:
    values = {}
    add_known_ctx(values, node.ctx)

    return AstNode(kind="Name", values={"id": node.id, **values})


def add_constant(s: AstSerializer, node: ast.Constant) -> AstNode:
    return AstNode(
        kind="Constant",
        values={"value": make_value(node.value)},
    )


def add_num(s: AstSerializer, node: ast.Num) -> AstNode:
    return AstNode(
        kind="Num",
        values={"n": make_number(node.value)},
    )


def add_str(s: AstSerializer, node: ast.Str) -> AstNode:
    return AstNode(kind="Str", values={"s": AstNodeValue(text=node.value)})


def add_raw_str(s: AstSerializer, node: str) -> AstNode:
    return AstNode(kind="Str", values={"s": AstNodeValue(text=node)})


def add_unary_op(s: AstSerializer, node: ast.UnaryOp) -> AstNode:
    return AstNode(
        kind="UnaryOp",
        values={"op": type(node.op).__name__},
        properties={"operand": s.serialize(node.operand)},
    )


def add_bin_op(s: AstSerializer, node: ast.BinOp) -> AstNode:
    return AstNode(
        kind="BinOp",
        values={"op": type(node.op).__name__},
        properties={
            "left": s.serialize(node.left),
            "right": s.serialize(node.right),
        },
    )


def add_compare(s: AstSerializer, node: ast.Compare) -> AstNode:
    return AstNode(
        kind="Compare",
        values={"ops": " ".join(type(op).__name__ for op in node.ops)},
        properties={"left": s.serialize(node.left)},
        children={
            "comparators": [s.serialize(comparator) for comparator in node.comparators]
        },
    )


def add_call(s: AstSerializer, node: ast.Call) -> AstNode:
    if not isinstance(node.func, ast.Name):
        raise Exception("Functino only support direct reference")

    return AstNode(
        kind="Call",
        values={"fn_name": node.func.id},
        children={"args": [s.serialize(arg) for arg in node.args]},
    )


def add_function(s: AstSerializer, node: ast.FunctionDef) -> AstNode:
    return AstNode(
        kind="FunctionDef",
        values={
            "name": node.name,
            "args": FunctionParams(positional_names=[a.arg for a in node.args.args]),
        },
        children={"body": [s.serialize(element) for element in node.body]},
    )


def add_return(s: AstSerializer, node: ast.Return) -> AstNode:
    properties: Dict[str, int] = {}

    if not node.value is None:
        properties["value"] = s.serialize(node.value)

    return AstNode(kind="Return", properties=properties)


def add_comprehension(s: AstSerializer, node: ast.comprehension) -> AstNode:
    return AstNode(
        kind="comprehension",
        values={"is_async": make_number(node.is_async)},
        properties={"iter": s.serialize(node.iter), "target": s.serialize(node.target)},
        children={"ifs": [s.serialize(element) for element in node.ifs]},
    )


def add_generator_exp(s: AstSerializer, node: ast.GeneratorExp) -> AstNode:
    return AstNode(
        kind="GeneratorExp",
        properties={"elt": s.serialize(node.elt)},
        children={
            "generators": [s.serialize(generator) for generator in node.generators]
        },
    )


def add_if(s: AstSerializer, node: ast.If) -> AstNode:
    return AstNode(
        kind="If",
        properties={"test": s.serialize(node.test)},
        children={
            "body": [s.serialize(element) for element in node.body],
            "orelse": [s.serialize(element) for element in node.orelse],
        },
    )


def add_subscript(s: AstSerializer, node: ast.Subscript) -> AstNode:
    return AstNode(
        kind="Subscript",
        properties={
            "value": s.serialize(node.value),
            "slice": s.serialize(node.slice.value),
        },
    )


def add_attribute(s: AstSerializer, node: ast.Attribute) -> AstNode:
    return AstNode(
        kind="Attribute",
        values={"attr": node.attr},
        properties={
            "value": s.serialize(node.value),
        },
    )


def add_assign(s: AstSerializer, node: ast.Assign) -> AstNode:
    return AstNode(
        kind="Assign",
        properties={"value": s.serialize(node.value)},
        children={"targets": [s.serialize(target) for target in node.targets]},
    )


def add_bool_op(s: AstSerializer, node: ast.BoolOp) -> AstNode:
    return AstNode(
        kind="BoolOp",
        values={"op": type(op).__name__},
        children={"values": [s.serialize(expr) for expr in node.values]},
    )


def add_bool_or(s: AstSerializer, node: ast.Or) -> AstNode:
    return AstNode(
        kind="Or",
        children={"values": [s.serialize(expr) for expr in node.values]},
    )


def add_bool_and(s: AstSerializer, node: ast.And) -> AstNode:
    return AstNode(
        kind="And",
        children={"values": [s.serialize(expr) for expr in node.values]},
    )


def add_complex_call(s: AstSerializer, node: ast.Call) -> AstNode:
    return AstNode(
        kind="Call",
        properties={"fn": s.serialize(node.func)},
        children={"args": [s.serialize(arg) for arg in node.args]},
    )


SIMPLE_AST_SERIALIZER: TypeSerializerMap = {
    ast.Module: add_trivial_module,
    ast.Expr: add_expr,
    ast.Name: add_name,
    ast.Constant: add_constant,
    ast.Num: add_num,
    ast.Str: add_str,
    str: add_raw_str,
    ast.UnaryOp: add_unary_op,
    ast.BinOp: add_bin_op,
    ast.Compare: add_compare,
    ast.Call: add_call,
}

FULL_AST_SERIALIZER: TypeSerializerMap = {
    **SIMPLE_AST_SERIALIZER,
    ast.FunctionDef: add_function,
    ast.Return: add_return,
    ast.GeneratorExp: add_generator_exp,
    ast.If: add_if,
    ast.Subscript: add_subscript,
    ast.Attribute: add_attribute,
    ast.Assign: add_assign,
    ast.BoolOp: add_bool_op,
    ast.Call: add_complex_call,
    ast.Module: add_module,
    ast.comprehension: add_comprehension,
}

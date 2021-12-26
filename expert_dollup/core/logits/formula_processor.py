from abc import ABC, abstractmethod
import ast
from ast import AST
from typing import Dict
from math import sqrt
from expert_dollup.core.domains import AstNode


class SafeguardDivision(ast.NodeTransformer):
    def visit_BinOp(self, node: ast.BinOp):
        if isinstance(node.op, ast.Div):
            return ast.Call(
                func=ast.Name(id="safe_div", ctx=ast.Load()),
                args=[
                    self.generic_visit(node.left),
                    self.generic_visit(node.right),
                ],
                keywords=[],
            )

        return self.generic_visit(node)


def serialize_ast(node: AST) -> AstNode:
    if isinstance(node, ast.Module):
        return AstNode(kind="Module", properties={"body": serialize_ast(node.body[0])})

    if isinstance(node, ast.Expr):
        return AstNode(kind="Expr", properties={"value": serialize_ast(node.value)})

    if isinstance(node, ast.Name):
        return AstNode(kind="Name", values={"id": node.id})

    if isinstance(node, ast.Constant):
        return AstNode(kind="Constant", values={"value": node.value})

    if isinstance(node, ast.Num):
        return AstNode(kind="Num", values={"n": node.n})

    if isinstance(node, ast.Str):
        return AstNode(kind="Str", values={"s": node.s})

    if isinstance(node, ast.UnaryOp):
        return AstNode(
            kind="UnaryOp",
            values={"op": type(node.op).__name__},
            properties={"operand": serialize_ast(node.operand)},
        )

    if isinstance(node, ast.BinOp):
        return AstNode(
            kind="BinOp",
            values={"op": type(node.op).__name__},
            properties={
                "left": serialize_ast(node.left),
                "right": serialize_ast(node.right),
            },
        )

    if isinstance(node, ast.Compare):
        return AstNode(
            kind="Compare",
            values={"ops": " ".join(type(op).__name__ for op in node.ops)},
            properties={"left": serialize_ast(node.left)},
            children={
                "comparators": [
                    serialize_ast(comparator) for comparator in node.comparators
                ]
            },
        )

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise Exception("Functino only support direct reference")

        return AstNode(
            kind="Call",
            values={"fn_name": node.func.id},
            children={"args": [serialize_ast(arg) for arg in node.args]},
        )

    raise Exception(f"Unsupported node {type(node)}")


def serialize_post_processed_expression(expression: str) -> dict:
    def replace_divisions(formula_ast: AST):
        return SafeguardDivision().visit(formula_ast)

    final_ast = replace_divisions(ast.parse(expression))
    ast_node = serialize_ast(final_ast)

    return ast_node.dict()


class ComputationUnit(ABC):
    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def units(self) -> Dict[str, "ComputationUnit"]:
        pass


def process_module_node(node: dict, unit: ComputationUnit):
    return dispatch(node["properties"]["body"], unit)


def process_expr_node(node: dict, unit: ComputationUnit):
    return dispatch(node["properties"]["value"], unit)


def process_name_node(node: dict, unit: ComputationUnit):
    name = node["values"]["id"]
    assert (
        name in unit.units
    ), f"{name} not part of formula {unit.name} which contains {unit.units.keys()}"
    values = unit.units[name]

    if len(values) == 1:
        return values[0].value, f"<{name}, {values[0].value}>"

    sum_result = sum(unit.value for unit in unit.units[name])

    return sum_result, f"sum(<{name}, {sum_result}>)"


def process_constant_node(node: dict, unit: ComputationUnit):
    value = node["values"]["value"]
    return value, f"{value}"


def process_num_node(node: dict, unit: ComputationUnit):
    value = node["values"]["n"]
    return value, f"{value}"


def process_str_node(node: dict, unit: ComputationUnit):
    value = node["values"]["a"]
    return value, f"{value}"


UNARY_OP_DISPATCH = {
    "UAdd": lambda operand, operand_details: (+operand, f"+{operand_details}"),
    "USub": lambda operand, operand_details: (-operand, f"-{operand_details}"),
    "Not": lambda operand, operand_details: (not operand, f"!{operand_details}"),
}


def process_unary_op_node(node: dict, unit: ComputationUnit):
    operand, operand_details = dispatch(node["properties"]["operand"], unit)
    op = node["values"]["op"]
    compute = UNARY_OP_DISPATCH.get(op)

    if compute is None:
        raise Exception("Unsupported unary op")

    return compute(operand, operand_details)


BiNARY_OP_DISPATCH = {
    "Add": lambda left, left_details, right, right_details: (
        left + right,
        f"{left_details} + {right_details}",
    ),
    "Sub": lambda left, left_details, right, right_details: (
        left - right,
        f"{left_details} - {right_details}",
    ),
    "Mult": lambda left, left_details, right, right_details: (
        left * right,
        f"{left_details} * {right_details}",
    ),
    "Div": lambda left, left_details, right, right_details: (
        safe_div(left, right),
        f"safe_div({left_details}, {right_details})",
    ),
}


def process_bin_op_node(node: dict, unit: ComputationUnit):
    left, left_details = dispatch(node["properties"]["left"], unit)
    right, right_details = dispatch(node["properties"]["right"], unit)
    op = node["values"]["op"]
    compute = BiNARY_OP_DISPATCH.get(op)

    if compute is None:
        raise Exception("Unsupported binary op")

    return compute(left, left_details, right, right_details)


COMPARATOR_DISPATCH = {
    "Eq": lambda left, left_details, right, right_details: (
        left == right,
        f"{left_details} == {right_details}",
    ),
    "NotEq": lambda left, left_details, right, right_details: (
        left != right,
        f"{left_details} != {right_details}",
    ),
    "Lt": lambda left, left_details, right, right_details: (
        left < right,
        f"{left_details} < {right_details}",
    ),
    "LtE": lambda left, left_details, right, right_details: (
        left < right,
        f"{left_details} <= {right_details}",
    ),
    "Gt": lambda left, left_details, right, right_details: (
        left > right,
        f"{left_details} > {right_details}",
    ),
    "GtE": lambda left, left_details, right, right_details: (
        left >= right,
        f"{left_details} >= {right_details}",
    ),
}


def process_compare_node(node: dict, unit: ComputationUnit):
    left, left_details = dispatch(node["properties"]["left"], unit)
    result = left
    details = f"{left_details}"
    ops = node["values"]["ops"].split()

    for comparator, op in zip(node["children"]["comparators"], ops):
        right, right_details = dispatch(comparator, unit)
        compute = COMPARATOR_DISPATCH.get(op)

        if compute is None:
            raise Exception("Unssuported comparator")

        result, details = compute(left, details, right, right_details)
        left = right

    return result, details


def safe_div(a, b):
    if b == 0:
        return 0

    return a / b


def process_call_node(node: dict, unit: ComputationUnit):
    args = []
    details = []

    for arg in node["children"]["args"]:
        result, calculation_details = dispatch(arg, unit)
        args.append(result)
        details.append(calculation_details)

    details_str = ", ".join(details)
    fn_id = node["values"]["fn_name"]

    if fn_id == "safe_div":
        return safe_div(*args), f"safe_div({details_str})"

    if fn_id == "sqrt":
        return sqrt(*args), f"sqrt({details_str})"

    raise Exception(f"Unknown function {fn_id}")


AST_NODE_PROCESSOR: Dict[str, callable] = {
    "Module": process_module_node,
    "Expr": process_expr_node,
    "Name": process_name_node,
    "Constant": process_constant_node,
    "Num": process_num_node,
    "Str": process_str_node,
    "UnaryOp": process_unary_op_node,
    "BinOp": process_bin_op_node,
    "Compare": process_compare_node,
    "Call": process_call_node,
}


def dispatch(node: dict, unit: ComputationUnit):
    return AST_NODE_PROCESSOR[node["kind"]](node, unit)
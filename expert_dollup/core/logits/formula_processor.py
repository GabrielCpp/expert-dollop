from abc import ABC, abstractmethod
import ast
from uuid import UUID
from ast import AST
from typing import Callable, Dict, Union, List, Any, Tuple
from expert_dollup.core.domains import AstNode, AstNodeValue, FlatAst
from decimal import Decimal
from dataclasses import dataclass


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


def make_number(value: Union[None, str, bytes, bool, int, float, complex, Decimal]):
    return AstNodeValue(number=Decimal("{:.6f}".format(value)))


def make_value(
    value: Union[None, str, bytes, bool, int, float, complex, Decimal]
) -> AstNodeValue:
    if isinstance(value, (float, int)):
        return make_number(value)

    if isinstance(value, str):
        return AstNodeValue(text=value)

    if isinstance(value, Decimal):
        return AstNodeValue(number=value)

    raise Exception(f"Unsupported type {type(value)} with value {value}")


class AstSerializer:
    def __init__(self):
        self.nodes = []

    def _add(self, node: AstNode) -> int:
        index = len(self.nodes)
        self.nodes.append(node)
        return index

    def serialize_ast(self, node: AST) -> FlatAst:
        root_index = self.serialize(node)
        return FlatAst(nodes=self.nodes, root_index=root_index)

    def serialize(self, node: AST) -> int:
        if isinstance(node, ast.Module):
            return self._add(
                AstNode(
                    kind="Module", properties={"body": self.serialize(node.body[0])}
                )
            )

        if isinstance(node, ast.Expr):
            return self._add(
                AstNode(kind="Expr", properties={"value": self.serialize(node.value)})
            )

        if isinstance(node, ast.Name):
            return self._add(AstNode(kind="Name", values={"id": node.id}))

        if isinstance(node, ast.Constant):
            return self._add(
                AstNode(
                    kind="Constant",
                    values={"value": make_value(node.value)},
                )
            )

        if isinstance(node, ast.Num):
            return self._add(
                AstNode(
                    kind="Num",
                    values={"n": make_number(node.value)},
                )
            )

        if isinstance(node, ast.Str):
            return self._add(
                AstNode(kind="Str", values={"s": AstNodeValue(text=node.value)})
            )

        if isinstance(node, ast.UnaryOp):
            return self._add(
                AstNode(
                    kind="UnaryOp",
                    values={"op": type(node.op).__name__},
                    properties={"operand": self.serialize(node.operand)},
                )
            )

        if isinstance(node, ast.BinOp):
            return self._add(
                AstNode(
                    kind="BinOp",
                    values={"op": type(node.op).__name__},
                    properties={
                        "left": self.serialize(node.left),
                        "right": self.serialize(node.right),
                    },
                )
            )

        if isinstance(node, ast.Compare):
            return self._add(
                AstNode(
                    kind="Compare",
                    values={"ops": " ".join(type(op).__name__ for op in node.ops)},
                    properties={"left": self.serialize(node.left)},
                    children={
                        "comparators": [
                            self.serialize(comparator)
                            for comparator in node.comparators
                        ]
                    },
                )
            )

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise Exception("Functino only support direct reference")

            return self._add(
                AstNode(
                    kind="Call",
                    values={"fn_name": node.func.id},
                    children={"args": [self.serialize(arg) for arg in node.args]},
                )
            )

        raise Exception(f"Unsupported node {type(node)}")


def serialize_post_processed_expression(expression: str) -> dict:
    def replace_divisions(formula_ast: AST):
        return SafeguardDivision().visit(formula_ast)

    final_ast = replace_divisions(ast.parse(expression))
    serializer = AstSerializer()
    flat_tree = serializer.serialize_ast(final_ast)

    return flat_tree.dict()


class ComputationUnit(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def node_id(self) -> UUID:
        pass

    @property
    @abstractmethod
    def units(self) -> Dict[str, "ComputationUnit"]:
        pass


@dataclass
class Calculation:
    details: str = ""
    index: int = 0

    def add(self, result, details) -> str:
        self.index = self.index + 1
        temp_name = f"temp{self.index}({result})"
        self.details = f"{self.details}\n{temp_name} = {details}"

        return temp_name

    def add_final(self, result, details) -> None:
        self.index = self.index + 1
        temp_name = f"\n<final_result, {result}>"
        self.details = f"{self.details}\n{temp_name} = {details}"


@dataclass
class ComputationScope:
    unit: ComputationUnit
    calc: Calculation
    nodes: List[dict]

    def get_property(self, node: dict, name: str) -> dict:
        return self.nodes[node["properties"][name]]

    def get_children(self, node, name) -> list:
        return [self.nodes[c] for c in node["children"][name]]


Result = Tuple[Any, str]


def process_module_node(node: dict, scope: ComputationScope):
    return dispatch(scope.get_property(node, "body"), scope)


def process_expr_node(node: dict, scope: ComputationScope):
    return dispatch(scope.get_property(node, "value"), scope)


def process_name_node(node: dict, scope: ComputationScope):
    name = node["values"]["id"]
    assert (
        name in scope.unit.units
    ), f"{name} not part of formula {scope.unit.name} which contains {scope.unit.units.keys()}"
    values = scope.unit.units[name]

    if len(values) == 1:
        return values[0].value, f"<{name}[{values[0].node_id}], {values[0].value}>"

    sum_result = sum(unit.value for unit in scope.unit.units[name])

    return sum_result, scope.calc.add(sum_result, f"sum({name})")


def process_constant_node(node: dict, scope: ComputationScope):
    value = node["values"]["value"]
    text = value["text"]
    enabled = value["enabled"]
    numeric = value["number"]

    if not numeric is None:
        real_value = Decimal(numeric)
    elif not enabled is None:
        real_value = enabled
    elif not text is None:
        real_value = text
    else:
        raise Exception("None is not supproted")

    return real_value, f"{real_value}"


def process_num_node(node: dict, scope: ComputationScope):
    value = node["values"]["n"]
    text = value["text"]
    enabled = value["enabled"]
    numeric = value["number"]

    if not numeric is None:
        real_value = Decimal(numeric)
    elif not enabled is None:
        real_value = enabled
    elif not text is None:
        real_value = text
    else:
        raise Exception("None is not supproted")

    return real_value, f"{real_value}"


def process_str_node(node: dict, scope: ComputationScope):
    value = node["values"]["a"]
    text = value["text"]
    enabled = value["enabled"]
    numeric = value["number"]

    if not numeric is None:
        real_value = Decimal(numeric)
    elif not enabled is None:
        real_value = enabled
    elif not text is None:
        real_value = text
    else:
        raise Exception("None is not supproted")

    return real_value, f"{real_value}"


UNARY_OP_DISPATCH = {
    "UAdd": lambda operand, operand_details: (+operand, f"+{operand_details}"),
    "USub": lambda operand, operand_details: (-operand, f"-{operand_details}"),
    "Not": lambda operand, operand_details: (not operand, f"!{operand_details}"),
}


def process_unary_op_node(node: dict, scope: ComputationScope):
    operand, operand_details = dispatch(scope.get_property(node, "operand"), scope)
    op = node["values"]["op"]
    compute = UNARY_OP_DISPATCH.get(op)

    if compute is None:
        raise Exception("Unsupported unary op")

    result, details = compute(operand, operand_details)
    return result, scope.calc.add(result, details)


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


def process_bin_op_node(node: dict, scope: ComputationScope):
    left, left_details = dispatch(scope.get_property(node, "left"), scope)
    right, right_details = dispatch(scope.get_property(node, "right"), scope)
    op = node["values"]["op"]
    compute = BiNARY_OP_DISPATCH.get(op)

    if compute is None:
        raise Exception("Unsupported binary op")

    result, details = compute(left, left_details, right, right_details)

    return result, scope.calc.add(result, details)


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


def process_compare_node(node: dict, scope: ComputationScope):
    left, left_details = dispatch(scope.get_property(node, "left"), scope)
    result = left
    details = f"{left_details}"
    ops = node["values"]["ops"].split()

    for comparator, op in zip(scope.get_children(node, "comparators"), ops):
        right, right_details = dispatch(comparator, scope)
        compute = COMPARATOR_DISPATCH.get(op)

        if compute is None:
            raise Exception("Unssuported comparator")

        result, details = compute(left, details, right, right_details)
        left = right

    result = Decimal(1 if result else 0)

    return result, scope.calc.add(result, details)


def safe_div(a: Decimal, b: Decimal) -> Decimal:
    assert isinstance(a, Decimal), f"{type(a)} -> {a}"
    assert isinstance(b, Decimal), f"{type(b)} -> {b}"

    if b.is_zero():
        return Decimal(0)

    return a / b


def process_call_node(node: dict, scope: ComputationScope) -> Result:
    args = []
    details: List[str] = []

    for arg in scope.get_children(node, "args"):
        result, calculation_details = dispatch(arg, scope)
        args.append(result)
        details.append(calculation_details)

    details_str = ", ".join(details)
    fn_id = node["values"]["fn_name"]

    if fn_id == "safe_div":
        result = safe_div(*args)
        details_str = f"safe_div({details_str})"
        return result, scope.calc.add(result, details_str)

    if fn_id == "sqrt":
        assert len(args) == 1
        result = args[0].sqrt()
        details_str = f"sqrt({details_str})"
        return result, scope.calc.add(result, details_str)

    raise Exception(f"Unknown function {fn_id}")


AST_NODE_PROCESSOR: Dict[str, Callable[[dict, ComputationScope], Result]] = {
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


def dispatch(node: dict, scope: ComputationScope) -> Result:
    return AST_NODE_PROCESSOR[node["kind"]](node, scope)


def compute(flat_tree: dict, unit: ComputationUnit) -> Result:
    calc = Calculation()
    nodes = flat_tree["nodes"]
    root_index = flat_tree["root_index"]
    node = nodes[root_index]
    scope = ComputationScope(unit=unit, calc=calc, nodes=nodes)

    result, details = dispatch(node, scope)
    calc.add_final(result, details)
    return result, calc.details

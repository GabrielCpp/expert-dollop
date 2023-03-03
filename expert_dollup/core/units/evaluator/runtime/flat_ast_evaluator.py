import ast
from uuid import UUID
from ast import AST
from typing import Callable, Dict, Union, List, Any, Tuple, Protocol
from decimal import Decimal
from dataclasses import dataclass
from typing_extensions import TypeAlias
from .exceptions import AstRuntimeError

PrimitiveWithNoneUnion = Union[bool, int, str, Decimal, None]
Result = Tuple[Any, str]


class AnyCallable(Protocol):
    def __call__(self, *args, **kwargs) -> Any:
        ...


class ReturnSignal(Exception):
    def __init__(self, value, details: str):
        Exception.__init__(self, "Evaluate return")
        self.value = value
        self.details = details


@dataclass
class Computation:
    value: PrimitiveWithNoneUnion = None
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


LexicalScope: TypeAlias = Dict[str, Computation]


def div_or_0(left, right) -> Decimal:
    try:
        return Decimal(left / right)
    except ZeroDivisionError:
        return 0


@dataclass
class ComputationContext:
    global_functions: Dict[str, AnyCallable]
    lexical_scopes: List[LexicalScope]
    calc: Computation
    nodes: List[dict]

    def append_scope(self, new_vars: dict) -> LexicalScope:
        if len(self.lexical_scopes) == 0:
            raise AstRuntimeError("No lexical scope in the context")

        lexical_scope = self.lexical_scopes[-1]
        new_lexical_scope = dict(lexical_scope)
        new_lexical_scope.update(new_vars)
        self.lexical_scopes.append(new_lexical_scope)

        return new_lexical_scope

    def assign(self, target, value) -> None:
        if len(self.lexical_scopes) == 0:
            raise AstRuntimeError("No lexical scope in the context")

        lexical_scope = self.lexical_scopes[-1]
        lexical_scope[target] = value

    def pop_scope(self) -> None:
        self.lexical_scopes.pop()

    def is_kind(self, node: dict, kind: str) -> bool:
        return node["kind"] == kind

    def get_function(self, name: str) -> AnyCallable:
        return self.global_functions[name]

    def has_property(self, node: dict, name: str) -> bool:
        return name in node["properties"]

    def get_property(self, node: dict, name: str) -> dict:
        return self.nodes[node["properties"][name]]

    def has_children(self, node, name) -> bool:
        return name in node["children"]

    def get_children(self, node, name) -> list:
        return [self.nodes[c] for c in node["children"][name]]

    def get_name(self, name: str) -> Computation:
        value = self.global_functions.get(name, None)

        if not value is None:
            return Computation(value=value)

        if len(self.lexical_scopes) == 0:
            raise AstRuntimeError("No lexical scope in the context")

        lexical_scope = self.lexical_scopes[-1]

        if not name in lexical_scope:
            raise AstRuntimeError(
                "Lexical scope is missing a name",
                names=list(lexical_scope.keys()),
                mssing_name=name,
            )

        return lexical_scope[name]


def coerce_decimal(value: PrimitiveWithNoneUnion) -> Decimal:
    if value is None:
        return Decimal(0)

    if isinstance(value, bool):
        return Decimal(int(value))

    if isinstance(value, (int, str)):
        return Decimal(value)

    return value


def process_module_node(node: dict, scope: ComputationContext) -> Result:
    if scope.has_property(node, "body"):
        return dispatch(scope.get_property(node, "body"), scope)

    body = scope.get_children(node, "body")
    result = None, ""

    for element in body:
        result = dispatch(element, scope)

    return result


def process_expr_node(node: dict, scope: ComputationContext):
    return dispatch(scope.get_property(node, "value"), scope)


def process_name_node(node: dict, scope: ComputationContext):
    name = node["values"]["id"]
    ctx = node["values"]["ctx"]

    if ctx == "Save":
        return name, name

    computation = scope.get_name(name)
    return computation.value, computation.details


def process_constant_node(node: dict, scope: ComputationContext):
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
        raise AstRuntimeError("None is not supproted")

    return real_value, f"{real_value}"


def process_num_node(node: dict, scope: ComputationContext):
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
        raise AstRuntimeError("None is not supproted")

    return real_value, f"{real_value}"


def process_str_node(node: dict, scope: ComputationContext):
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
        raise AstRuntimeError("None is not supproted")

    return real_value, f"{real_value}"


UNARY_OP_DISPATCH = {
    "UAdd": lambda operand, operand_details: (+operand, f"+{operand_details}"),
    "USub": lambda operand, operand_details: (-operand, f"-{operand_details}"),
    "Not": lambda operand, operand_details: (not operand, f"!{operand_details}"),
}


def process_unary_op_node(node: dict, scope: ComputationContext):
    operand, operand_details = dispatch(scope.get_property(node, "operand"), scope)
    op = node["values"]["op"]
    compute = UNARY_OP_DISPATCH.get(op)

    if compute is None:
        raise AstRuntimeError("Unsupported unary op", op=op)

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
        div_or_0(left, right),
        f"safe_div({left_details}, {right_details})",
    ),
}


def process_bin_op_node(node: dict, scope: ComputationContext):
    left, left_details = dispatch(scope.get_property(node, "left"), scope)
    right, right_details = dispatch(scope.get_property(node, "right"), scope)
    op = node["values"]["op"]
    compute = BiNARY_OP_DISPATCH.get(op)

    if compute is None:
        raise AstRuntimeError("Unsupported binary op", op=op)

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


def process_compare_node(node: dict, scope: ComputationContext):
    left, left_details = dispatch(scope.get_property(node, "left"), scope)
    result = left
    details = f"{left_details}"
    ops = node["values"]["ops"].split()

    for comparator, op in zip(scope.get_children(node, "comparators"), ops):
        right, right_details = dispatch(comparator, scope)
        compute = COMPARATOR_DISPATCH.get(op)

        if compute is None:
            raise AstRuntimeError("Unssuported comparator", op=op)

        result, details = compute(left, details, right, right_details)
        left = right

    result = Decimal(1 if result else 0)

    return result, scope.calc.add(result, details)


def process_call_node(node: dict, scope: ComputationContext) -> Result:
    args = []
    details: List[str] = []

    for arg in scope.get_children(node, "args"):
        result, calculation_details = dispatch(arg, scope)
        args.append(Computation(details=calculation_details, value=result))
        details.append(calculation_details)

    details_str = ", ".join(details)

    if "fn_name" in node["values"]:
        fn_id = node["values"]["fn_name"]
        fn = scope.global_functions.get(fn_id)

        if fn is None:
            raise AstRuntimeError(f"Unknown function name", name=fn_id)

        result = fn(scope, args)
        details_str = f"{fn_id}({details_str})"
        return result, scope.calc.add(result, details_str)

    fn_node = scope.get_property(node, "fn")
    fn, _ = dispatch(fn_node, scope)

    if getattr(fn, "__name__", None) == "_compute_function":
        result, details_str = fn(scope, args)
    else:
        args = [a.value for a in args]
        result = fn(*args)

    return result, scope.calc.add(result, details_str)


def process_subscript_node(node: dict, scope: ComputationContext) -> Result:
    value_node = scope.get_property(node, "value")
    value, value_details = dispatch(value_node, scope)
    slice_node = scope.get_property(node, "slice")
    index, slice_details = dispatch(slice_node, scope)
    result = value[index]

    return result, scope.calc.add(result, f"{value_details}[{slice_details}]")


def process_function_def_node(node: dict, scope: ComputationContext) -> Result:
    args_name = node["values"]["args"]["positional_names"]
    body = scope.get_children(node, "body")

    def _compute_function(scope: ComputationContext, args: list):
        scope.append_scope(dict(zip(args_name, args)))
        value, details = None, ""

        try:
            for element in body:
                if scope.is_kind(element, "Return"):
                    value_node = scope.get_property(element, "value")
                    value, details = dispatch(value_node, scope)
                    break

                value, details = dispatch(element, scope)
        except ReturnSignal as r:
            return r.value, r.details
        finally:
            scope.pop_scope()

        return value, details

    name = node["values"]["name"]
    scope.global_functions[name] = _compute_function
    return _compute_function, ""


def process_if_node(node: dict, scope: ComputationContext) -> Result:
    test = scope.get_property(node, "test")
    result, details = dispatch(test, scope)

    if result:
        body = scope.get_children(node, "body")
        for element in body:
            dispatch(element, scope)
    else:
        orelse = scope.get_children(node, "orelse")
        for element in orelse:
            dispatch(element, scope)

    return result, f"if({details})"


def process_return_node(node: dict, scope: ComputationContext) -> Result:
    if scope.has_property(node, "value"):
        condition = scope.get_property(node, "value")
        return_value, details = dispatch(condition, scope)
    else:
        return_value, details = None, ""

    raise ReturnSignal(return_value, details)


def proces_comprehension_node(node: dict, scope: ComputationContext) -> Result:
    iter_node = scope.get_property(node, "iter")
    iterable, _ = dispatch(iter_node, scope)

    target_node = scope.get_property(node, "target")
    target, _ = dispatch(target_node, scope)

    def _next_value():
        for value in iterable:
            scope.assign(target, Computation(value))
            yield value

    return _next_value, "<comphension>"


def process_generator_exp_node(node: dict, scope: ComputationContext) -> Result:
    generators_nodes = scope.get_children(node, "generators")
    generators = [dispatch(g, scope) for g in generators_nodes]
    values = []

    elt_node = scope.get_property(node, "elt")

    for gen, _ in generators:
        for _ in gen():
            local_value, _ = dispatch(elt_node, scope)
            values.append(local_value)

    return values, ""


def process_assign_node(node: dict, scope: ComputationContext) -> Result:
    targets_nodes = scope.get_children(node, "targets")
    targets = [dispatch(t, scope) for t in targets_nodes]

    value_node = scope.get_property(node, "value")
    value, details = dispatch(value_node, scope)
    c = Computation(value=value, details=details)

    for target, _ in targets:
        scope.assign(target, c)

    return value, f" = {value}"


def process_attribute_node(node: dict, scope: ComputationContext) -> Result:
    value_node = scope.get_property(node, "value")
    value, details = dispatch(value_node, scope)
    attr = node["values"]["attr"]
    return getattr(value, attr), f"{details}.{attr}"


def process_bool_op_node(node: dict, scope: ComputationContext) -> Result:
    op = node["values"]["op"]

    if op == "Or":
        x = False
        values_nodes = scope.get_children(node, "values")

        for expr in values_nodes:
            value, _ = dispatch(expr, scope)
            x = x or value

        return x, ""

    elif op == "And":
        x = True
        values_nodes = scope.get_children(node, "values")

        for expr in values_nodes:
            value, _ = dispatch(expr, scope)
            x = x and value

        return x, ""

    raise AstRuntimeError("Unsupported BoolOp", op=op)


AST_NODE_PROCESSOR: Dict[str, Callable[[dict, ComputationContext], Result]] = {
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
    "Subscript": process_subscript_node,
    "FunctionDef": process_function_def_node,
    "Return": process_return_node,
    "GeneratorExp": process_generator_exp_node,
    "If": process_if_node,
    "Attribute": process_attribute_node,
    "Assign": process_assign_node,
    "BoolOp": process_bool_op_node,
    "comprehension": proces_comprehension_node,
}


def dispatch(node: dict, scope: ComputationContext) -> Result:
    return AST_NODE_PROCESSOR[node["kind"]](node, scope)


class FlatAstEvaluator:
    def __init__(self, global_functions: Dict[str, AnyCallable] = {}):
        self.global_functions = global_functions

    def compute(self, flat_tree: dict, lexical_scope: LexicalScope) -> Result:
        calc = Computation()
        nodes = flat_tree["nodes"]
        root_index = flat_tree["root_index"]
        node = nodes[root_index]
        scope = ComputationContext(
            lexical_scopes=[lexical_scope],
            calc=calc,
            nodes=nodes,
            global_functions=self.global_functions,
        )

        result, details = dispatch(node, scope)
        calc.add_final(result, details)
        return result, calc.details

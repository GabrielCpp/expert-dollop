import ast
from ast import *
from expert_dollup.core.domains.formula import FieldNode
from typing import Awaitable, List, Union
from math import sqrt
from uuid import UUID
from collections import defaultdict
from expert_dollup.core.domains import (
    Formula,
    FormulaDetails,
    FormulaCachedResult,
    FormulaNode,
)
from expert_dollup.infra.services import (
    FormulaService,
    ProjectNodeService,
    FormulaCacheService,
)


def safe_div(a, b):
    if b == 0:
        return 0

    return a / b


class FormulaInjector:
    def __init__(self):
        self.unit_map: Dict[str, Union["FormulaUnit", "FieldUnit"]] = defaultdict(list)
        self.units: List["FormulaUnit"] = []

    def add_unit(
        self, path: List[UUID], name: str, unit: Union["FormulaUnit", "FieldUnit"]
    ):
        for item in path:
            self.unit_map[f"{item}.{name}"].append(unit)

        self.unit_map[name].append(unit)
        self.unit_map[f"{unit.node.id}.{name}"].append(unit)

        if isinstance(unit, FormulaUnit):
            self.units.append(unit)

    def get_unit(self, path: List[UUID], name: str):
        for id in reversed(path):
            unit_id = f"{id}.{name}"

            if unit_id in self.unit_map:
                return self.unit_map[unit_id]

        if name in self.unit_map:
            return self.unit_map[name]

        return []


class FormulaUnit:
    def __init__(
        self,
        node: FormulaNode,
        dependencies: List[str],
        formula_injector: FormulaInjector,
    ):
        self.node = node
        self.formula_injector = formula_injector
        self._dependencies = dependencies

    @property
    def value(self):
        self.units = {
            name: self.formula_injector.get_unit(self.node.path, name)
            for name in self._dependencies
        }

        result, calculation_details = self._compute(self.node.expression.body[0])
        self.calculation_details = calculation_details

        return result

    def _compute(self, node):
        if isinstance(node, ast.Expr):
            return self._compute(node.value)

        if isinstance(node, ast.Name):
            values = self.units[node.id]

            if len(values) == 1:
                return values[0].value, f"<{node.id}, {values[0].value}>"

            sum_result = sum(unit.value for unit in self.units[node.id])

            return sum_result, f"sum(<{node.id}, {sum_result}>)"

        if isinstance(node, ast.Constant):
            return node.value, f"{node.value}"

        if isinstance(node, ast.Num):
            return node.n, f"{node.n}"

        if isinstance(node, ast.Str):
            return node.s, f"{node.s}"

        if isinstance(node, ast.UnaryOp):
            operand = self._compute(node.operand)

            if isinstance(node.op, ast.UAdd):
                return +operand, f"+{operand}"

            if isinstance(node.op, ast.USub):
                return -operand, f"-{operand}"

            if isinstance(node.op, ast.Not):
                return not operand, f"!{operand}"

            raise Exception("Unsupported unary op")

        if isinstance(node, ast.BinOp):
            left, left_details = self._compute(node.left)
            right, right_details = self._compute(node.right)

            if isinstance(node.op, ast.Add):
                return left + right, f"{left_details} + {right_details}"

            if isinstance(node.op, ast.Sub):
                return left - right, f"{left_details} - {right_details}"

            if isinstance(node.op, ast.Mult):
                return left * right, f"{left_details} * {right_details}"

            if isinstance(node.op, ast.Div):
                return (
                    safe_div(left, right),
                    f"safe_div({left_details}, {right_details})",
                )

            raise Exception("Unsupported binary op")

        if isinstance(node, ast.Compare):
            left, left_details = self._compute(node.left)
            result = left
            details = f"{left_details}"

            for comparator, op in zip(node.comparators, node.ops):
                right, right_details = self._compute(comparator)

                if isinstance(op, ast.Eq):
                    result = left == right
                    details = details + f" == {right_details}"

                elif isinstance(op, ast.NotEq):
                    result = left != right
                    details = details + f" != {right_details}"

                elif isinstance(op, ast.Lt):
                    result = left < right
                    details = details + f" < {right_details}"

                elif isinstance(op, ast.LtE):
                    result = left <= right
                    details = details + f" <= {right_details}"

                elif isinstance(op, ast.Gt):
                    result = left > right
                    details = details + f" > {right_details}"

                elif isinstance(op, ast.GtE):
                    result = left >= right
                    details = details + f" >= {right_details}"
                else:
                    raise Exception("Unssuported comparator")

                left = right

            return result, details

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise Exception("Functino only support direct reference")

            args = []
            details = []

            for arg in node.args:
                result, calculation_details = self._compute(arg)
                args.append(result)
                details.append(calculation_details)

            details_str = ", ".join(details)

            if node.func.id == "safe_div":
                return safe_div(*args), f"safe_div({details_str})"

            if node.func.id == "sqrt":
                return sqrt(*args), f"sqrt({details_str})"

            raise Exception(f"Unknown function {node.func.id}")

        raise Exception(f"Unsupported node {type(node)}")


class FieldUnit:
    def __init__(self, node: FieldNode, value: Union[bool, str, int, float]):
        self.node = node
        self.value = value


class FormulaVisitor(ast.NodeVisitor):
    whithelisted_node = set(
        [
            "Module",
            "Expr",
            "BinOp",
            "Num",
            "Sub",
            "Add",
            "Mult",
            "Div",
            "Call",
            "Subscript",
            "Attribute",
            "Index",
        ]
    )

    whithelisted_fn_names = set(["sqrt", "sin", "cos", "tan", "abs"])

    def __init__(self):
        self.var_names = set()
        self.fn_names = set()

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_Call(self, node: ast.Name):
        self.fn_names.add(node.func.id)

    def visit_Name(self, node: ast.Name):
        self.var_names.add(node.id)

    def visit_Load(self, node):
        pass


class SafeguardDivision(ast.NodeTransformer):
    def visit_BinOp(self, node: BinOp):
        if isinstance(node.op, Div):
            return Call(
                func=ast.Name(id="safe_div", ctx=ast.Load()),
                args=[
                    self.generic_visit(node.left),
                    self.generic_visit(node.right),
                ],
                keywords=[],
            )

        return self.generic_visit(node)


class FormulaResolver:
    def __init__(
        self,
        formula_service: FormulaService,
        project_node_service: ProjectNodeService,
        formula_cache_service: FormulaCacheService,
    ):
        self.formula_service = formula_service
        self.project_node_service = project_node_service
        self.formula_cache_service = formula_cache_service

    async def parse(self, formula: Formula) -> FormulaDetails:
        formula_ast = ast.parse(formula.expression)
        visitor = FormulaVisitor()
        visitor.visit(formula_ast)

        if formula.name in visitor.var_names:
            raise Exception()

        for name in visitor.fn_names:
            if not name in FormulaVisitor.whithelisted_fn_names:
                raise Exception()

        formulas = await self.formula_service.get_formulas_by_name(visitor.var_names)
        fields = await self.formula_service.get_fields_by_name(visitor.var_names)
        unkowns_names = (
            set(visitor.var_names) - set(formulas.keys()) - set(fields.keys())
        )

        if len(unkowns_names) > 0:
            raise Exception()

        formula_details = FormulaDetails(
            formula=formula,
            formula_dependencies=formulas,
            field_dependencies=fields,
            formula_ast=formula_ast,
        )

        formula_details.formula.generated_ast = self.generate_formula_unit(
            formula_details
        )

        return formula_details

    def generate_formula_unit(self, formula_details: FormulaDetails):
        return SafeguardDivision().visit(formula_details.formula_ast)

    async def compute_all_project_formula(
        self, project_id: UUID, project_definition_id: UUID
    ) -> Awaitable[List[FormulaCachedResult]]:
        injector = FormulaInjector()
        fields = await self.project_node_service.get_all_fields(project_id)

        for node in fields:
            injector.add_unit(node.path, node.name, FieldUnit(node, node.expression))

        formulas: List[
            FormulaNode
        ] = await self.formula_service.get_all_project_formula_ast(
            project_id, project_definition_id
        )

        formula_id_to_name_map = {}

        for node in fields:
            formula_id_to_name_map[node.type_id] = node.name

        for node in formulas:
            formula_id_to_name_map[node.formula_id] = node.name

        for node in formulas:
            injector.add_unit(
                node.path,
                node.name,
                FormulaUnit(
                    node,
                    [
                        formula_id_to_name_map[dependency_id]
                        for dependency_id in node.dependencies
                    ],
                    injector,
                ),
            )

        cached_results = [
            FormulaCachedResult(
                project_id=project_id,
                formula_id=unit.node.formula_id,
                node_id=unit.node.id,
                result=unit.value,
                calculation_details=unit.calculation_details,
            )
            for unit in injector.units
        ]

        await self.formula_cache_service.repopulate(project_id, cached_results)

        return cached_results

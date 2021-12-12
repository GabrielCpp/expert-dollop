import ast
from ast import *
from expert_dollup.core.domains.formula import FieldNode, FormulaCachedResultFilter
from typing import List, Union, Dict
from math import sqrt
from uuid import UUID
from collections import defaultdict
from expert_dollup.core.domains import (
    Formula,
    FormulaExpression,
    FormulaCachedResult,
    ComputedFormula,
    FormulaDependencyGraph,
    FormulaDependency,
    FormulaPluckFilter,
    NodePluckFilter,
)
from expert_dollup.core.domains.project_definition_node import ValueUnion
from expert_dollup.core.domains.project_node import ProjectNode
from expert_dollup.infra.services import (
    FormulaService,
    ProjectNodeService,
    FormulaCacheService,
    ProjectDefinitionNodeService,
)
from expert_dollup.core.queries import Plucker


def safe_div(a, b):
    if b == 0:
        return 0

    return a / b


class FormulaInjector:
    def __init__(self):
        self.unit_map: Dict[str, Union["FormulaUnit", "FieldUnit"]] = defaultdict(list)
        self.units: List["FormulaUnit"] = []

    def add_unit(self, unit: Union["FormulaUnit", "FieldUnit"]):
        for item in unit.path:
            self.unit_map[f"{item}.{unit.name}"].append(unit)

        self.unit_map[unit.name].append(unit)
        self.unit_map[f"{unit.node_id}.{unit.name}"].append(unit)

        if isinstance(unit, FormulaUnit):
            self.units.append(unit)

    def get_unit(self, node_id: UUID, path: List[UUID], name: str):
        unit_id = f"{node_id}.{name}"

        if unit_id in self.unit_map:
            return self.unit_map[unit_id]

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
        computed_formula: ComputedFormula,
        formula_id_to_name_map: Dict[UUID, str],
        node_id_to_name_map: Dict[UUID, str],
        formula_injector: FormulaInjector,
    ):
        self._computed_formula = computed_formula
        self._formula_id_to_name_map = formula_id_to_name_map
        self._node_id_to_name_map = node_id_to_name_map
        self._formula_injector = formula_injector

    @property
    def dependencies(self) -> List[str]:
        merged_dependencies = []

        for dependency in self._computed_formula.formula.dependency_graph.formulas:
            dependency_name = self._formula_id_to_name_map.get(
                dependency.target_type_id
            )

            assert (
                not dependency_name is None
            ), f"Missing id {dependency.target_type_id} in dependencies"
            merged_dependencies.append(dependency_name)

        for dependency in self._computed_formula.formula.dependency_graph.nodes:
            dependency_name = self._node_id_to_name_map.get(dependency.target_type_id)
            assert (
                not dependency_name is None
            ), f"Missing id {dependency.target_type_id} in dependencies"
            merged_dependencies.append(dependency_name)

        return merged_dependencies

    @property
    def node_id(self) -> UUID:
        return self._computed_formula.node.id

    @property
    def path(self) -> List[UUID]:
        return self._computed_formula.node.path

    @property
    def name(self) -> str:
        return self._computed_formula.formula.name

    @property
    def expression_body(self) -> AST:
        return self._computed_formula.final_ast.body[0]

    @property
    def formula_id(self) -> UUID:
        return self._computed_formula.formula.id

    @property
    def value(self):
        self.units = {
            name: self._formula_injector.get_unit(self.node_id, self.path, name)
            for name in self.dependencies
        }

        result, calculation_details = self._compute(self.expression_body)
        self.calculation_details = calculation_details

        return result

    def _compute(self, node):
        if isinstance(node, ast.Expr):
            return self._compute(node.value)

        if isinstance(node, ast.Name):
            assert node.id in self.units, f"{node.id } not in {self.units}"
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
    def __init__(self, node: ProjectNode):
        self._node = node

    @property
    def value(self) -> ValueUnion:
        return self._node.value

    @property
    def node_id(self) -> UUID:
        return self._node.id

    @property
    def path(self) -> List[UUID]:
        return self._node.path

    @property
    def name(self) -> str:
        return self._node.type_name


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
        project_definition_node_service: ProjectDefinitionNodeService,
        formula_cache_service: FormulaCacheService,
        formulas_plucker: Plucker[FormulaService],
        nodes_plucker: Plucker[ProjectNodeService],
    ):
        self.formula_service = formula_service
        self.project_node_service = project_node_service
        self.project_definition_node_service = project_definition_node_service
        self.formula_cache_service = formula_cache_service
        self.formulas_plucker = formulas_plucker
        self.nodes_plucker = nodes_plucker

    async def parse(self, formula_expression: FormulaExpression) -> Formula:
        formula_ast = ast.parse(formula_expression.expression)
        visitor = FormulaVisitor()
        visitor.visit(formula_ast)

        if formula_expression.name in visitor.var_names:
            all_formulas = ",".join(visitor.var_names)
            raise Exception(
                f"Formua {formula_expression.name} not found in [{all_formulas}]"
            )

        for name in visitor.fn_names:
            if not name in FormulaVisitor.whithelisted_fn_names:
                fn_names = ",".join(FormulaVisitor.whithelisted_fn_name)
                raise Exception(f"Function {name} not found in [{fn_names}]")

        formulas_by_name = await self.formula_service.get_formulas_by_name(
            formula_expression.project_def_id, visitor.var_names
        )
        fields_by_name = await self.project_definition_node_service.get_fields_by_name(
            formula_expression.project_def_id, visitor.var_names
        )
        unkowns_names = (
            set(visitor.var_names)
            - set(formulas_by_name.keys())
            - set(fields_by_name.keys())
        )

        if len(unkowns_names) > 0:
            unkowns_names_joined = ",".join(unkowns_names)
            raise Exception(
                f"There unknown name in expression [{unkowns_names_joined}] in {formula_expression.name}"
            )

        formula = Formula(
            id=formula_expression.id,
            project_def_id=formula_expression.project_def_id,
            attached_to_type_id=formula_expression.attached_to_type_id,
            name=formula_expression.name,
            expression=formula_expression.expression,
            dependency_graph=FormulaDependencyGraph(
                formulas=[
                    FormulaDependency(target_type_id=formula_id)
                    for formula_id in formulas_by_name.values()
                ],
                nodes=[
                    FormulaDependency(target_type_id=field_id)
                    for field_id in fields_by_name.values()
                ],
            ),
        )

        return formula

    async def compute_all_project_formula(
        self, project_id: UUID, project_definition_id: UUID
    ) -> List[FormulaCachedResult]:
        injector = FormulaInjector()
        formula_id_to_name_map: Dict[UUID, str] = {}
        nodes = await self.project_node_service.get_all_fields(project_id)
        node_id_to_name_map: Dict[UUID, str] = {
            node.type_id: node.type_name for node in nodes
        }

        for node in nodes:
            injector.add_unit(FieldUnit(node))

        computed_formulas = await self.get_all_project_formula_ast(
            project_id, project_definition_id
        )

        for computed_formula in computed_formulas:
            unit = FormulaUnit(
                computed_formula,
                formula_id_to_name_map,
                node_id_to_name_map,
                injector,
            )
            formula_id_to_name_map[unit.formula_id] = unit.name
            injector.add_unit(unit)

        cached_results = [
            FormulaCachedResult(
                project_id=project_id,
                formula_id=unit.formula_id,
                node_id=unit.node_id,
                result=unit.value,
                calculation_details=unit.calculation_details,
            )
            for unit in injector.units
        ]

        await self.formula_cache_service.repopulate(project_id, cached_results)

        return cached_results

    async def get_all_project_formula_ast(
        self, project_id: UUID, project_definition_id: UUID
    ) -> List[ComputedFormula]:
        def post_process_ast(formula_ast: AST):
            return SafeguardDivision().visit(formula_ast)

        def build_computed_formula(
            result: FormulaCachedResult,
            formulas_by_id: Dict[UUID, Formula],
            nodes_by_id: Dict[UUID, ProjectNode],
        ):
            formula = formulas_by_id[result.formula_id]
            node = nodes_by_id[result.node_id]
            final_ast = post_process_ast(ast.parse(formula.expression))

            return ComputedFormula(
                formula=formula,
                result=result,
                node=node,
                final_ast=final_ast,
            )

        results = await self.formula_cache_service.find_by(
            FormulaCachedResultFilter(project_id=project_id)
        )

        formulas = await self.formulas_plucker.plucks(
            lambda ids: FormulaPluckFilter(ids=ids),
            list(set(result.formula_id for result in results)),
        )
        formulas_by_id = {formula.id: formula for formula in formulas}

        nodes = await self.nodes_plucker.plucks(
            lambda ids: NodePluckFilter(ids=ids),
            [result.node_id for result in results],
        )
        nodes_by_id = {node.id: node for node in nodes}

        return [
            build_computed_formula(result, formulas_by_id, nodes_by_id)
            for result in results
        ]

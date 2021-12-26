import ast
from functools import cached_property
from expert_dollup.core.domains.formula import FormulaInstanceFilter
from typing import List, Union, Dict, Set
from uuid import UUID
from collections import defaultdict
from expert_dollup.core.domains import (
    Formula,
    FormulaExpression,
    FormulaInstance,
    FormulaDependencyGraph,
    FormulaDependency,
)
from expert_dollup.core.domains.project_definition_node import ValueUnion
from expert_dollup.core.domains.project_node import ProjectNode
from expert_dollup.infra.services import (
    FormulaService,
    ProjectNodeService,
    FormulaInstanceService,
    ProjectDefinitionNodeService,
)
from expert_dollup.core.queries import Plucker
from expert_dollup.core.logits import FormulaVisitor
import expert_dollup.core.logits.formula_processor as formula_processor


class FormulaInjector:
    def __init__(self):
        self.unit_map: Dict[str, List[Union["FormulaUnit", "FieldUnit"]]] = defaultdict(
            list
        )
        self.units: List["FormulaUnit"] = []

    def add_unit(self, unit: Union["FormulaUnit", "FieldUnit"]) -> None:
        for item in unit.path:
            self.unit_map[f"{item}.{unit.name}"].append(unit)

        self.unit_map[unit.name].append(unit)
        self.unit_map[f"{unit.node_id}.{unit.name}"].append(unit)

        if isinstance(unit, FormulaUnit):
            self.units.append(unit)

    def get_unit(
        self, node_id: UUID, path: List[UUID], name: str
    ) -> List[Union["FormulaUnit", "FieldUnit"]]:
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
        formula_instance: FormulaInstance,
        final_ast: dict,
        formula_injector: FormulaInjector,
    ):
        self._formula_instance = formula_instance
        self._final_ast = final_ast
        self._formula_injector = formula_injector

    @property
    def dependencies(self) -> List[str]:
        return self._formula_instance.formula_dependencies

    @property
    def node_id(self) -> UUID:
        return self._formula_instance.node_id

    @property
    def path(self) -> List[UUID]:
        return self._formula_instance.node_path

    @property
    def name(self) -> str:
        return self._formula_instance.formula_name

    @property
    def formula_id(self) -> UUID:
        return self._formula_instance.formula_id

    @cached_property
    def computed(self) -> FormulaInstance:
        self.units = {
            name: self._formula_injector.get_unit(self.node_id, self.path, name)
            for name in self.dependencies
        }

        result, calculation_details = formula_processor.dispatch(self._final_ast, self)

        self._formula_instance.result = result
        self._formula_instance.calculation_details = calculation_details

        return self._formula_instance

    @property
    def value(self):
        return self.computed.result


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


class FormulaResolver:
    def __init__(
        self,
        formula_service: FormulaService,
        project_node_service: ProjectNodeService,
        project_definition_node_service: ProjectDefinitionNodeService,
        formula_instance_service: FormulaInstanceService,
        formulas_plucker: Plucker[FormulaService],
        nodes_plucker: Plucker[ProjectNodeService],
    ):
        self.formula_service = formula_service
        self.project_node_service = project_node_service
        self.project_definition_node_service = project_definition_node_service
        self.formula_instance_service = formula_instance_service
        self.formulas_plucker = formulas_plucker
        self.nodes_plucker = nodes_plucker

    async def parse_many(self, formula_expressions: List[FormulaExpression]) -> Formula:
        def get_names(expression: str):
            formula_ast = ast.parse(expression)
            visitor = FormulaVisitor()
            visitor.visit(formula_ast)
            return visitor

        project_def_id = formula_expressions[0].project_def_id
        for formula_expression in formula_expressions:
            if formula_expression.project_def_id != project_def_id:
                raise Exception(
                    "When importing a batch of formula they must all have same project_def_id"
                )

        formulas_id_by_name = await self.formula_service.get_formulas_id_by_name(
            project_def_id
        )
        fields_id_by_name = (
            await self.project_definition_node_service.get_fields_id_by_name(
                project_def_id
            )
        )

        for formula_expression in formula_expressions:
            if formula_expression.name in formulas_id_by_name:
                raise Exception(f"Formula {formula_expression.name} already exists")

            formulas_id_by_name[formula_expression.name] = formula_expression.id

        formula_dependencies: Dict[str, Set[str]] = {
            formula_expression.name: get_names(formula_expression.expression)
            for formula_expression in formula_expressions
        }

        known_formula_names = set(formulas_id_by_name.keys())
        known_field_names = set(fields_id_by_name.keys())

        for formula_name, visitor in formula_dependencies.items():
            if formula_name in visitor.var_names:
                raise Exception(f"Formula {formula_name} is self dependant")

            for name in visitor.fn_names:
                if not name in FormulaVisitor.whithelisted_fn_names:
                    fn_names = ",".join(FormulaVisitor.whithelisted_fn_name)
                    raise Exception(f"Function {name} not found in [{fn_names}]")

            unkowns_names = visitor.var_names - known_formula_names - known_field_names

            if len(unkowns_names) > 0:
                unkowns_names_joined = ",".join(unkowns_names)
                raise Exception(
                    f"There unknown name in expression [{unkowns_names_joined}] in {formula_expression.name}"
                )

        formulas = [
            Formula(
                id=formula_expression.id,
                project_def_id=formula_expression.project_def_id,
                attached_to_type_id=formula_expression.attached_to_type_id,
                name=formula_expression.name,
                expression=formula_expression.expression,
                final_ast=formula_processor.serialize_post_processed_expression(
                    formula_expression.expression
                ),
                dependency_graph=FormulaDependencyGraph(
                    formulas=[
                        FormulaDependency(
                            target_type_id=formulas_id_by_name[name], name=name
                        )
                        for name in formula_dependencies[
                            formula_expression.name
                        ].var_names
                        if name in known_formula_names
                    ],
                    nodes=[
                        FormulaDependency(
                            target_type_id=fields_id_by_name[name], name=name
                        )
                        for name in formula_dependencies[
                            formula_expression.name
                        ].var_names
                        if name in known_field_names
                    ],
                ),
            )
            for formula_expression in formula_expressions
        ]

        return formulas

    async def parse(self, formula_expression: FormulaExpression) -> Formula:
        formula_ast = ast.parse(formula_expression.expression)
        visitor = FormulaVisitor()
        visitor.visit(formula_ast)

        if formula_expression.name in visitor.var_names:
            raise Exception(f"Formua {formula_expression.name} is self dependant")

        for name in visitor.fn_names:
            if not name in FormulaVisitor.whithelisted_fn_names:
                fn_names = ",".join(FormulaVisitor.whithelisted_fn_name)
                raise Exception(f"Function {name} not found in [{fn_names}]")

        formulas_id_by_name = await self.formula_service.get_formulas_id_by_name(
            formula_expression.project_def_id, visitor.var_names
        )
        fields_id_by_name = (
            await self.project_definition_node_service.get_fields_id_by_name(
                formula_expression.project_def_id, visitor.var_names
            )
        )
        unkowns_names = (
            set(visitor.var_names)
            - set(formulas_id_by_name.keys())
            - set(fields_id_by_name.keys())
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
            final_ast=formula_processor.serialize_post_processed_expression(
                formula_expression.expression
            ),
            dependency_graph=FormulaDependencyGraph(
                formulas=[
                    FormulaDependency(target_type_id=formula_id, name=name)
                    for name, formula_id in formulas_id_by_name.items()
                ],
                nodes=[
                    FormulaDependency(target_type_id=field_id, name=name)
                    for name, field_id in fields_id_by_name.items()
                ],
            ),
        )

        return formula

    async def compute_all_project_formula(
        self, project_id: UUID, project_def_id: UUID
    ) -> List[FormulaInstance]:
        injector = FormulaInjector()
        nodes = await self.project_node_service.get_all_fields(project_id)

        for node in nodes:
            injector.add_unit(FieldUnit(node))

        formula_instances = await self.formula_instance_service.find_by(
            FormulaInstanceFilter(project_id=project_id)
        )

        formula_final_ast_by_formula_id = (
            await self.formula_service.find_formula_final_ast_by_formula_id(
                project_def_id
            )
        )

        for formula_instance in formula_instances:
            injector.add_unit(
                FormulaUnit(
                    formula_instance,
                    formula_final_ast_by_formula_id[formula_instance.formula_id],
                    injector,
                )
            )

        cached_results = [unit.computed for unit in injector.units]

        return cached_results

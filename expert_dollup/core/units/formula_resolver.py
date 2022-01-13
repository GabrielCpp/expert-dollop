from typing import List, Dict, Set, Tuple
from uuid import UUID
from asyncio import gather
from expert_dollup.shared.database_services import log_execution_time_async, StopWatch
from expert_dollup.core.domains import (
    Formula,
    FormulaExpression,
    FormulaDependencyGraph,
    FormulaDependency,
    UnitInstanceCache,
    FormulaFilter,
)
from expert_dollup.infra.services import (
    FormulaService,
    ProjectNodeService,
    ProjectDefinitionNodeService,
)
from expert_dollup.core.builders import UnitInstanceBuilder
from expert_dollup.core.logits import (
    FormulaVisitor,
    FormulaInjector,
    FormulaUnit,
    FieldUnit,
)
import expert_dollup.core.logits.formula_processor as formula_processor


class FormulaResolver:
    def __init__(
        self,
        formula_service: FormulaService,
        project_node_service: ProjectNodeService,
        project_definition_node_service: ProjectDefinitionNodeService,
        unit_instance_builder: UnitInstanceBuilder,
    ):
        self.formula_service = formula_service
        self.project_node_service = project_node_service
        self.project_definition_node_service = project_definition_node_service
        self.unit_instance_builder = unit_instance_builder

    async def parse_many(self, formula_expressions: List[FormulaExpression]) -> Formula:
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
            formula_expression.name: FormulaVisitor.get_names(
                formula_expression.expression
            )
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
        visitor = FormulaVisitor.get_names(formula_expression.expression)

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

    @log_execution_time_async
    async def compute_all_project_formula(
        self, project_id: UUID, project_def_id: UUID
    ) -> FormulaInjector:
        injector = FormulaInjector()

        with StopWatch("Fetching formula data"):
            nodes, formulas = await gather(
                self.project_node_service.get_all_fields(project_id),
                self.formula_service.find_by(
                    FormulaFilter(project_def_id=project_def_id)
                ),
            )

        formula_by_id = {formula.id: formula for formula in formulas}
        unit_instances = self.unit_instance_builder.build_with_fields(formulas, nodes)

        for node in nodes:
            injector.add_unit(FieldUnit(node))

        for formula_instance in unit_instances:
            formula = formula_by_id[formula_instance.formula_id]
            injector.add_unit(
                FormulaUnit(
                    formula_instance,
                    formula.dependency_graph.dependencies,
                    formula.final_ast,
                    injector,
                )
            )

        with StopWatch("Computing formulas"):
            injector.precompute()

        return injector

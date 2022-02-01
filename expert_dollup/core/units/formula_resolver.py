from typing import List, Dict, Set
from uuid import UUID
from asyncio import gather
from expert_dollup.core.domains.formula import (
    StagedFormula,
    StagedFormulas,
    StagedFormulasKey,
)
from expert_dollup.shared.database_services import log_execution_time_async, StopWatch
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.exceptions import RessourceNotFound
from expert_dollup.shared.starlette_injection import LoggerFactory
from expert_dollup.core.domains import (
    Formula,
    FormulaExpression,
    FormulaDependencyGraph,
    FormulaDependency,
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
        stage_formulas_storage: ObjectStorage[StagedFormulas, StagedFormulasKey],
        logger: LoggerFactory,
    ):
        self.formula_service = formula_service
        self.project_node_service = project_node_service
        self.project_definition_node_service = project_definition_node_service
        self.unit_instance_builder = unit_instance_builder
        self.stage_formulas_storage = stage_formulas_storage
        self.logger = logger.create(__name__)

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
                    f"There unknown name ({unkowns_names_joined}) in expression  in {formula_expression.name}"
                )

        formulas = [
            Formula(
                id=formula_expression.id,
                project_def_id=formula_expression.project_def_id,
                attached_to_type_id=formula_expression.attached_to_type_id,
                name=formula_expression.name,
                expression=formula_expression.expression,
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

    @staticmethod
    def stage_formulas(formulas: List[Formula]) -> StagedFormulas:
        return [
            StagedFormula(
                id=formula.id,
                project_def_id=formula.project_def_id,
                attached_to_type_id=formula.attached_to_type_id,
                name=formula.name,
                expression=formula.expression,
                dependency_graph=formula.dependency_graph,
                final_ast=formula_processor.serialize_post_processed_expression(
                    formula.expression
                ),
            )
            for formula in formulas
        ]

    async def build_staged_formulas(self, project_def_id: UUID) -> StagedFormulas:
        formulas = await self.formula_service.find_by(
            FormulaFilter(project_def_id=project_def_id)
        )

        return FormulaResolver.stage_formulas(formulas)

    async def refresh_staged_formulas_cache(
        self, project_def_id: UUID
    ) -> StagedFormulas:
        staged_formulas = await self.build_staged_formulas(project_def_id)
        await self.stage_formulas_storage.save(
            StagedFormulasKey(project_def_id), staged_formulas
        )
        return staged_formulas

    @log_execution_time_async
    async def get_staged_formulas(self, project_def_id: UUID) -> StagedFormulas:
        try:
            staged_formulas = await self.stage_formulas_storage.load(
                StagedFormulasKey(project_def_id)
            )
        except RessourceNotFound:
            staged_formulas = await self.refresh_staged_formulas_cache(project_def_id)

        return staged_formulas

    @log_execution_time_async
    async def compute_all_project_formula(
        self, project_id: UUID, project_def_id: UUID
    ) -> FormulaInjector:
        injector = FormulaInjector()

        with StopWatch(self.logger, "Fetching formula data"):
            nodes, staged_formulas = await gather(
                self.project_node_service.get_all_fields(project_id),
                self.get_staged_formulas(project_def_id),
            )

        formula_by_id = {formula.id: formula for formula in staged_formulas}
        unit_instances = self.unit_instance_builder.build_with_fields(
            staged_formulas, nodes
        )

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

        with StopWatch(self.logger, "Computing formulas"):
            injector.precompute()

        return injector

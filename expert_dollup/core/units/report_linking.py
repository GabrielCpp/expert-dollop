from abc import ABC, abstractmethod
from typing import Iterable, List, Dict, Tuple
from uuid import UUID
from decimal import Decimal
from collections import defaultdict
from dataclasses import dataclass
from asyncio import gather
from expert_dollup.shared.database_services import CollectionService
from expert_dollup.core.logits import FormulaInjector
from .formula_resolver import FormulaResolver
from .report_row_cache import ReportRowCache
from expert_dollup.core.exceptions import (
    ReportGenerationError,
    AstEvaluationError,
)
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services.time_it import log_execution_time_async
from expert_dollup.shared.starlette_injection import Clock, LoggerFactory
from .expression_evaluator import ExpressionEvaluator

FORMULA_BUCKET_NAME = "formula"
COLUMNS_BUCKET_NAME = "columns"
INTERNAL_BUCKET_NAME = "internal"


def round_number(number: Decimal, digits: int, method: str) -> Decimal:
    assert method == "truncate", "method is the only method supported"
    stepper = Decimal(10.0 ** digits)
    return Decimal(int(stepper * Decimal(number))) / stepper


def group_by_key(elements: Iterable, key: callable) -> dict:
    element_by_key = defaultdict(list)

    for element in elements:
        element_by_key[key(element)].append(element)

    return element_by_key


@dataclass
class LinkingData:
    report_definition: ReportDefinition
    project_details: ProjectDetails
    unit_instances: UnitInstanceCache
    injector: FormulaInjector
    datasheet_elements_by_id: Dict[UUID, DatasheetElement]


class ReportEvaluationContext:
    def __init__(
        self, expression_evaluator: ExpressionEvaluator, injector: FormulaInjector
    ):
        self.expression_evaluator = expression_evaluator
        self.injector = injector

    def evaluate_row(self, expression, row, rows):
        try:
            return self.expression_evaluator.evaluate(
                expression,
                {
                    "row": row,
                    "rows": rows,
                    "round_number": round_number,
                    "sum": sum,
                    "injector": self.injector,
                },
            )
        except AstEvaluationError as e:
            raise ReportGenerationError(
                f"Error while evaluating expression",
                expression=expression,
                row=row,
                **e.props,
            ) from e

    def evaluate(self, expression, scope):
        try:
            return self.expression_evaluator.evaluate(
                expression,
                scope,
            )
        except AstEvaluationError as e:
            raise ReportGenerationError(
                f"Error while evaluating expression",
                expression=expression,
                **e.props,
            ) from e


class JoinStep(ABC):
    @abstractmethod
    def apply(self, row: ReportRowDict) -> List[ReportRowDict]:
        pass


class MutateStep(ABC):
    @abstractmethod
    def apply(self, row: ReportRowDict) -> None:
        pass


class ProjectionStep(ABC):
    @abstractmethod
    def apply(self, rows: List[ReportRowDict]) -> List[ReportRowDict]:
        pass


@dataclass
class ReportGeneration:
    join_steps: List[JoinStep]
    mutate_steps: List[MutateStep]
    projection_steps: List[ProjectionStep]

    def apply_steps(
        self,
        rows: List[ReportRowDict],
    ) -> List[ReportRowDict]:
        for join_step in self.join_steps:
            new_rows: List[ReportRowDict] = []

            for row in rows:
                step_rows = join_step.apply(row)
                new_rows.extend(step_rows)

            rows = new_rows

        for mutate_step in self.mutate_steps:
            for row in rows:
                mutate_step.apply(row)

        for projection_step in self.projection_steps:
            rows = projection_step.apply(rows)

        return rows


class JoinFormulaUnitInstances(JoinStep):
    def __init__(self, linking_data: LinkingData):
        report_definition = linking_data.report_definition
        self.element_attribute = report_definition.structure.datasheet_attribute
        self.formula_attribute = report_definition.structure.formula_attribute
        self.unit_instances_by_def_id = (
            JoinFormulaUnitInstances.get_unit_instances_by_def_id(
                linking_data.unit_instances
            )
        )

    @staticmethod
    def get_unit_instances_by_def_id(
        unit_instances: UnitInstanceCache,
    ) -> Dict[UUID, UnitInstanceCache]:
        formula_instances = [
            unit_instance
            for unit_instance in unit_instances
            if not unit_instance.formula_id is None
            and (
                not isinstance(unit_instance.result, Decimal)
                or unit_instance.result > 0
            )
        ]

        return group_by_key(formula_instances, lambda x: x.formula_id)

    def apply(self, row: ReportRowDict) -> List[ReportRowDict]:
        element_def_id = self.element_attribute.get(row)
        assert isinstance(element_def_id, UUID)
        formula_id = self.formula_attribute.get(row)
        assert isinstance(formula_id, UUID)

        if not formula_id in self.unit_instances_by_def_id:
            return []

        return [
            {**row, FORMULA_BUCKET_NAME: formula_instance.report_dict}
            for formula_instance in self.unit_instances_by_def_id[formula_id]
        ]


class DatasheetElementInstanceAssignation(MutateStep):
    def __init__(self, linking_data: LinkingData):
        structure = linking_data.report_definition.structure
        self.element_attribute = structure.datasheet_attribute
        self.datasheet_bucket_name = structure.datasheet_attribute.attribute_name
        self.elements_by_id = linking_data.datasheet_elements_by_id
        self.datasheet_selection_alias = structure.datasheet_selection_alias

    def apply(self, row: ReportRowDict) -> None:
        element_def_id = self.element_attribute.get(row)
        element_dict = self.elements_by_id[element_def_id].report_dict
        element_def_dict = row[self.datasheet_selection_alias]
        row[self.datasheet_bucket_name] = {**element_def_dict, **element_dict}


class GroupDigestAssignation(MutateStep):
    def __init__(
        self, linking_data: LinkingData, evaluation_context: ReportEvaluationContext
    ):
        self.evaluation_context = evaluation_context
        self.structure = linking_data.report_definition.structure
        footprint_columns = {
            g.attribute_name
            for g in self.structure.group_by
            if g.bucket_name == COLUMNS_BUCKET_NAME
        }

        self.first_pass_columns = (
            self.structure.columns
            if len(footprint_columns) == 0
            else [
                column
                for column in self.structure.columns
                if column.name in footprint_columns or not column.is_visible
            ]
        )

    def apply(self, row: ReportRowDict) -> None:
        columns = {}
        row[COLUMNS_BUCKET_NAME] = columns

        for column in self.first_pass_columns:
            columns[column.name] = self.evaluation_context.evaluate_row(
                column.expression, row, None
            )

        group_id = "/".join(
            attribute_bucket.get(row) for attribute_bucket in self.structure.group_by
        )

        row[INTERNAL_BUCKET_NAME] = {"group_digest": group_id}


class GroupedColumnProjection(ProjectionStep):
    def __init__(
        self, linking_data: LinkingData, evaluation_context: ReportEvaluationContext
    ):
        self.evaluation_context = evaluation_context
        report_definition = linking_data.report_definition
        footprint_columns = {
            g.attribute_name
            for g in report_definition.structure.group_by
            if g.bucket_name == COLUMNS_BUCKET_NAME
        }

        first_pass_columns = (
            report_definition.structure.columns
            if len(footprint_columns) == 0
            else [
                column
                for column in report_definition.structure.columns
                if column.name in footprint_columns or not column.is_visible
            ]
        )

        first_pass_column_names = {
            first_pass_column.name for first_pass_column in first_pass_columns
        }

        self.second_pass_column = (
            []
            if len(footprint_columns) == 0
            else [
                column
                for column in report_definition.structure.columns
                if not column.name in first_pass_column_names
            ]
        )

        if len(self.second_pass_column) == 0:
            raise Exception("Group by require at least one aggregate")

    def apply(self, rows: List[ReportRowDict]) -> List[ReportRowDict]:
        new_rows: List[ReportRowDict] = []
        rows_by_group = group_by_key(
            rows, lambda x: x[INTERNAL_BUCKET_NAME]["group_digest"]
        )

        for grouped_rows in rows_by_group.values():
            current_row = grouped_rows[0]
            columns = current_row[COLUMNS_BUCKET_NAME]
            rows = [row for row in grouped_rows]

            for column in self.second_pass_column:
                columns[column.name] = self.evaluation_context.evaluate_row(
                    column.expression, current_row, rows
                )

            if columns["cost"] != 0:
                new_rows.append(current_row)

        return new_rows


class RowOrdering(ProjectionStep):
    def __init__(self, linking_data: LinkingData):
        self.structure = linking_data.report_definition.structure

    def get_row_order_tuple(self, row: ReportRowDict) -> list:
        return [
            attribute_bucket.get(row) for attribute_bucket in self.structure.order_by
        ]

    def apply(self, rows: List[ReportRowDict]) -> List[ReportRowDict]:
        rows.sort(key=self.get_row_order_tuple)

        for index, row in enumerate(rows):
            row[INTERNAL_BUCKET_NAME]["order_index"] = index

        return rows


class ReportBuilder:
    def __init__(
        self,
        clock: Clock,
        linking_data: LinkingData,
        evaluation_context: ReportEvaluationContext,
    ):
        self.clock = clock
        self.linking_data = linking_data
        self.evaluation_context = evaluation_context

    def build(self, rows: List[ReportRowDict]) -> Report:
        formula_attribute = (
            self.linking_data.report_definition.structure.formula_attribute
        )
        element_attribute = (
            self.linking_data.report_definition.structure.datasheet_attribute
        )
        stage_summary = self.linking_data.report_definition.structure.stage_summary
        report_summary = self.linking_data.report_definition.structure.report_summary
        columns = self.linking_data.report_definition.structure.columns

        def get_unit(row, unit):
            return unit.get(row) if isinstance(unit, AttributeBucket) else unit

        report_rows = [
            ReportRow(
                node_id=row[FORMULA_BUCKET_NAME]["node_id"],
                formula_id=formula_attribute.get(row),
                element_def_id=element_attribute.get(row),
                child_reference_id=self.linking_data.datasheet_elements_by_id[
                    element_attribute.get(row)
                ].child_element_reference,
                columns=[
                    ReportColumn(
                        value=row[COLUMNS_BUCKET_NAME][column.name],
                        unit=get_unit(row, column.unit),
                    )
                    for column in columns
                ],
                row=row,
            )
            for row in rows
        ]

        report_rows_by_stage = group_by_key(report_rows, stage_summary.label.get)
        stages = [
            ReportStage(
                rows=rows,
                summary=ComputedValue(
                    value=self.evaluation_context.evaluate_row(
                        stage_summary.summary.expression,
                        None,
                        rows,
                    ),
                    label=label,
                    unit=get_unit(rows[0], stage_summary.summary.unit),
                ),
            )
            for label, rows in report_rows_by_stage.items()
        ]

        metas = {}
        scope = {
            "stages": stages,
            "round_number": round_number,
            "sum": sum,
            "injector": self.linking_data.injector,
            "metas": metas,
        }
        summaries = [
            ComputedValue(
                label=summary.name,
                value=metas.setdefault(
                    summary.name,
                    self.evaluation_context.evaluate(
                        summary.expression,
                        scope,
                    ),
                ),
                unit=summary.unit,
            )
            for summary in report_summary
        ]

        return Report(
            stages=stages, summaries=summaries, creation_date_utc=self.clock.utcnow()
        )


class ReportLinking:
    def __init__(
        self,
        datasheet_element_service: CollectionService[DatasheetElement],
        expression_evaluator: ExpressionEvaluator,
        report_row_cache_builder: ReportRowCache,
        formula_resolver: FormulaResolver,
        clock: Clock,
        logger: LoggerFactory,
    ):
        self.datasheet_element_service = datasheet_element_service
        self.expression_evaluator = expression_evaluator
        self.report_row_cache_builder = report_row_cache_builder
        self.formula_resolver = formula_resolver
        self.clock = clock
        self.logger = logger.create(__name__)

    @log_execution_time_async
    async def link_report(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
    ) -> Report:
        rows, linking_data = await self._preload_data(
            report_definition, project_details
        )
        evaluation_context = ReportEvaluationContext(
            self.expression_evaluator, linking_data.injector
        )
        report_generation = ReportGeneration(
            join_steps=[JoinFormulaUnitInstances(linking_data)],
            mutate_steps=[
                DatasheetElementInstanceAssignation(linking_data),
                GroupDigestAssignation(linking_data, evaluation_context),
            ],
            projection_steps=[
                GroupedColumnProjection(linking_data, evaluation_context),
                RowOrdering(linking_data),
            ],
        )

        rows = report_generation.apply_steps(rows)
        return ReportBuilder(self.clock, linking_data, evaluation_context).build(rows)

    @log_execution_time_async
    async def _preload_data(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
    ) -> Tuple[ReportRowsCache, LinkingData]:

        rows, injector, datasheet_elements = await gather(
            self.report_row_cache_builder.refresh_cache(report_definition),
            self.formula_resolver.compute_all_project_formula(
                project_details.id, project_details.project_definition_id
            ),
            self.datasheet_element_service.find_by(
                DatasheetElementFilter(
                    datasheet_id=project_details.datasheet_id,
                    ordinal=0,
                )
            ),
        )

        datasheet_elements_by_id = {
            datasheet_element.element_def_id: datasheet_element
            for datasheet_element in datasheet_elements
        }

        return rows, LinkingData(
            report_definition=report_definition,
            project_details=project_details,
            unit_instances=injector.unit_instances,
            injector=injector,
            datasheet_elements_by_id=datasheet_elements_by_id,
        )

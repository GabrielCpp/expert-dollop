from typing import List, Dict
from uuid import UUID
from decimal import Decimal
from collections import defaultdict, OrderedDict
from itertools import groupby, chain
from dataclasses import dataclass
from asyncio import gather
from hashlib import sha3_256
from expert_dollup.infra.services import DatasheetElementService
from expert_dollup.core.logits import FormulaInjector
from .formula_resolver import FormulaResolver
from .report_row_cache import ReportRowCache
from expert_dollup.core.exceptions import (
    ReportGenerationError,
    AstEvaluationError,
)
from expert_dollup.core.domains import *
from expert_dollup.shared.database_services.time_it import log_execution_time_async
from expert_dollup.shared.starlette_injection import Clock
from .expression_evaluator import ExpressionEvaluator
from expert_dollup.shared.database_services import log_execution_time

FORMULA_BUCKET_NAME = "formula"
COLUMNS_BUCKET_NAME = "columns"


def round_number(number: Decimal, digits: int, method: str) -> Decimal:
    assert method == "truncate", "method is the only method supported"
    stepper = Decimal(10.0 ** digits)
    return Decimal(int(stepper * Decimal(number))) / stepper


@dataclass
class LinkingData:
    report_definition: ReportDefinition
    project_details: ProjectDetails
    unit_instances: UnitInstanceCache
    injector: FormulaInjector
    datasheet_elements_by_id: Dict[UUID, DatasheetElement]


class ReportLinking:
    def __init__(
        self,
        datasheet_element_service: DatasheetElementService,
        expression_evaluator: ExpressionEvaluator,
        report_row_cache_builder: ReportRowCache,
        formula_resolver: FormulaResolver,
        clock: Clock,
    ):
        self.datasheet_element_service = datasheet_element_service
        self.expression_evaluator = expression_evaluator
        self.report_row_cache_builder = report_row_cache_builder
        self.formula_resolver = formula_resolver
        self.clock = clock

    @log_execution_time_async
    async def link_report(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
    ) -> Report:

        rows, linking_data = await self._preload_data(
            report_definition, project_details
        )

        steps = [
            self._join_row_cache_with_unit_instances,
            self._fill_datasheet_element_in_rows,
            self._fill_row_columns,
            self._fill_row_order,
            self._fill_ordered_columns,
        ]

        for step in steps:
            rows = step(rows, linking_data)

        stages = self._build_stage_groups(rows, linking_data)
        summaries = self._build_report_summary(linking_data, stages)

        return Report(
            stages=stages, summaries=summaries, creation_date_utc=self.clock.utcnow()
        )

    @log_execution_time_async
    async def _preload_data(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
    ) -> LinkingData:

        rows, injector, datasheet_elements = await gather(
            self.report_row_cache_builder.refresh_cache(report_definition),
            self.formula_resolver.compute_all_project_formula(
                project_details.id, project_details.project_def_id
            ),
            self.datasheet_element_service.find_by(
                DatasheetElementFilter(
                    datasheet_id=project_details.datasheet_id,
                    child_element_reference=zero_uuid(),
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

    @log_execution_time
    def _join_row_cache_with_unit_instances(
        self, rows, linking_data: LinkingData
    ) -> List[ReportRow]:
        new_rows: List[ReportRow] = []

        report_definition = linking_data.report_definition
        element_attribute = report_definition.structure.datasheet_attribute
        formula_attribute = report_definition.structure.formula_attribute
        null_uuid = zero_uuid()

        formula_instances = [
            unit_instance
            for unit_instance in linking_data.unit_instances
            if not unit_instance.formula_id is None
            and (
                not isinstance(unit_instance.result, Decimal)
                or unit_instance.result > 0
            )
        ]
        formula_instances.sort(key=lambda x: x.formula_id)
        unit_instances_by_def_id: Dict[UUID, UnitInstanceCache] = {
            formula_id: list(values)
            for formula_id, values in groupby(
                formula_instances, key=lambda x: x.formula_id
            )
        }

        for row in rows:
            element_def_id = element_attribute.get(row)
            assert isinstance(element_def_id, UUID)
            formula_id = formula_attribute.get(row)
            assert isinstance(formula_id, UUID)

            if not formula_id in unit_instances_by_def_id:
                continue

            unit_instances = unit_instances_by_def_id[formula_id]

            new_rows.extend(
                ReportRow(
                    group_digest="",
                    node_id=formula_instance.node_id,
                    formula_id=formula_instance.formula_id,
                    element_def_id=element_def_id,
                    order_index=0,
                    child_reference_id=null_uuid,
                    columns=[],
                    row={**row, FORMULA_BUCKET_NAME: formula_instance.report_dict},
                )
                for formula_instance in unit_instances
            )

        return new_rows

    @log_execution_time
    def _fill_datasheet_element_in_rows(
        self, report_rows: List[ReportRow], linking_data: LinkingData
    ) -> List[ReportRow]:
        datasheet_bucket_name = (
            linking_data.report_definition.structure.datasheet_attribute.attribute_name
        )
        elements_by_id = linking_data.datasheet_elements_by_id

        for report_row in report_rows:
            element_dict = elements_by_id[report_row.element_def_id].report_dict
            report_row.row[datasheet_bucket_name] = element_dict

        return report_rows

    @log_execution_time
    def _fill_row_columns(
        self, report_rows: List[ReportRow], linking_data: LinkingData
    ) -> List[ReportRow]:
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

        second_pass_column = (
            []
            if len(footprint_columns) == 0
            else [
                column
                for column in report_definition.structure.columns
                if not column.name in first_pass_column_names
            ]
        )

        if len(second_pass_column) == 0:
            raise Exception("Group by require at least one aggregate")

        for report_row in report_rows:
            columns = {}
            report_row.row[COLUMNS_BUCKET_NAME] = columns

            for column in first_pass_columns:
                columns[column.name] = self._evaluate(
                    column.expression, report_row.row, None, linking_data.injector
                )

            group_id = "/".join(
                attribute_bucket.get(report_row.row)
                for attribute_bucket in report_definition.structure.group_by
            )

            report_row.group_digest = sha3_256(group_id.encode("utf8")).hexdigest()

        rows_by_group = defaultdict(list)

        for report_row in report_rows:
            rows_by_group[report_row.group_digest].append(report_row)

        grouped_rows = defaultdict(list)

        for group_report_rows in rows_by_group.values():
            rows = [group_report_row.row for group_report_row in group_report_rows]
            report_row = group_report_rows[0]
            columns = report_row.row[COLUMNS_BUCKET_NAME]

            for column in second_pass_column:
                columns[column.name] = self._evaluate(
                    column.expression, report_row.row, rows, linking_data.injector
                )

            if columns["cost"] != 0:
                stage = report_definition.structure.stage_summary.label.get(
                    report_row.row
                )
                grouped_rows[stage].append(report_row)

        return list(chain(*grouped_rows.values()))

    @log_execution_time
    def _fill_row_order(
        self, report_rows: List[ReportRow], linking_data: LinkingData
    ) -> List[ReportRow]:
        report_definition = linking_data.report_definition

        def get_row_order_tuple(report_row: ReportRow) -> list:
            ordering = []
            for attribute_bucket in report_definition.structure.order_by:
                value = attribute_bucket.get(report_row.row)
                ordering.append(value)

            return ordering

        report_rows.sort(key=get_row_order_tuple)

        for index, report_row in enumerate(report_rows):
            report_row.order_index = index

        return report_rows

    @log_execution_time
    def _build_stage_groups(
        self, report_rows: List[ReportRow], linking_data: LinkingData
    ) -> List[ReportStage]:
        groups = OrderedDict()
        report_definition = linking_data.report_definition
        stage_groups = []

        for report_row in report_rows:
            key = report_definition.structure.stage_summary.label.get(report_row.row)

            if not key in groups:
                groups[key] = []

            groups[key].append(report_row)

        for label, rows in groups.items():
            value = self._evaluate(
                report_definition.structure.stage_summary.summary.expression,
                None,
                rows,
                None,
            )

            stage_groups.append(
                ReportStage(
                    rows=rows, summary=ComputedValue(value=value, label=label, unit="$")
                )
            )

        return stage_groups

    @log_execution_time
    def _fill_ordered_columns(
        self, report_rows: List[ReportRow], linking_data: LinkingData
    ) -> List[ReportRow]:
        report_definition = linking_data.report_definition
        columns = report_definition.structure.columns

        for report_row in report_rows:
            for column in columns:
                unit = (
                    column.unit.get(report_row.row)
                    if isinstance(column.unit, AttributeBucket)
                    else column.unit
                )

                report_row.columns.append(
                    ReportColumn(
                        value=report_row.row[COLUMNS_BUCKET_NAME][column.name],
                        unit=unit,
                    )
                )

        return report_rows

    def _build_report_summary(
        self, linking_data: LinkingData, stages
    ) -> List[ComputedValue]:
        metas = {}
        summaries: List[ComputedValue] = []

        for summary in linking_data.report_definition.structure.report_summary:
            value = self.expression_evaluator.evaluate(
                summary.expression,
                {
                    "stages": stages,
                    "round_number": round_number,
                    "sum": sum,
                    "injector": linking_data.injector,
                    "metas": metas,
                },
            )
            metas[summary.name] = value
            summaries.append(
                ComputedValue(
                    label=summary.name,
                    value=value,
                    unit=summary.unit,
                )
            )

        return summaries

    def _evaluate(self, expression, row, rows_group, injector):
        try:
            return self.expression_evaluator.evaluate(
                expression,
                {
                    "row": row,
                    "rows": rows_group,
                    "round_number": round_number,
                    "sum": sum,
                    "injector": injector,
                },
            )
        except AstEvaluationError as e:
            raise ReportGenerationError(
                f"Error while evaluating expression",
                expression=expression,
                row=row,
                **e.props,
            ) from e

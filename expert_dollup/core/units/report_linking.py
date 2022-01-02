from typing import List, Dict, Optional
from uuid import UUID
from decimal import Decimal
from collections import defaultdict, OrderedDict
from itertools import groupby, chain
from dataclasses import dataclass
from hashlib import sha3_256
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.queries import Plucker
from expert_dollup.infra.services import DatasheetElementService
from expert_dollup.core.logits import FormulaInjector, FrozenUnit
from expert_dollup.core.exceptions import (
    ReportGenerationError,
    AstEvaluationError,
    RessourceNotFound,
)
from expert_dollup.core.domains import *
from expert_dollup.shared.starlette_injection import Clock
from .expression_evaluator import ExpressionEvaluator


def round_number(number: Decimal, digits: int, method: str) -> Decimal:
    assert method == "truncate", "method is the only method supported"
    stepper = Decimal(10.0 ** digits)
    return Decimal(int(stepper * Decimal(number))) / stepper


@dataclass
class LinkingData:
    report_definition: ReportDefinition
    project_details: ProjectDetails
    unit_instances: UnitInstanceCache
    old_report: Optional[Report]
    injector: FormulaInjector


class ReportLinking:
    def __init__(
        self,
        report_def_row_cache: ObjectStorage[ReportRowsCache, ReportRowKey],
        report_storage: ObjectStorage[Report, ReportKey],
        unit_instance_service: ObjectStorage[UnitInstanceCache, UnitInstanceCacheKey],
        datasheet_element_plucker: Plucker[DatasheetElementService],
        expression_evaluator: ExpressionEvaluator,
        clock: Clock,
    ):
        self.report_def_row_cache = report_def_row_cache
        self.unit_instance_service = unit_instance_service
        self.report_storage = report_storage
        self.datasheet_element_plucker = datasheet_element_plucker
        self.expression_evaluator = expression_evaluator
        self.clock = clock

    async def link_report(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
    ) -> Report:
        linking_data = await self._preload_data(report_definition, project_details)
        rows = await self.report_def_row_cache.load(
            ReportRowKey(
                project_def_id=report_definition.project_def_id,
                report_definition_id=report_definition.id,
            )
        )

        new_rows = self._join_row_cache_with_unit_instances(rows, linking_data)
        await self._fill_datasheet_element_in_rows(new_rows, linking_data)
        new_rows = self._fill_row_columns(new_rows, linking_data)
        new_rows = self._fill_row_order(new_rows, report_definition)
        stages = self._build_stage_groups(new_rows, report_definition)

        return Report(stages=stages, creation_date_utc=self.clock.utcnow())

    async def _preload_data(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
    ) -> LinkingData:
        unit_instances = await self.unit_instance_service.load(
            UnitInstanceCacheKey(project_id=project_details.id)
        )

        injector = FormulaInjector()
        for unit_instance in unit_instances:
            injector.add_unit(FrozenUnit(unit_instance))

        try:
            old_report = await self.report_storage.load(
                ReportKey(
                    project_id=project_details.id,
                    report_definition_id=report_definition.id,
                )
            )
        except RessourceNotFound:
            old_report = None

        return LinkingData(
            old_report=old_report,
            report_definition=report_definition,
            project_details=project_details,
            unit_instances=unit_instances,
            injector=injector,
        )

    def _join_row_cache_with_unit_instances(
        self, rows, linking_data: LinkingData
    ) -> List[ReportRow]:
        new_rows: List[ReportRow] = []

        report_definition = linking_data.report_definition
        element_attribute = report_definition.structure.datasheet_attribute
        formula_attribute = report_definition.structure.formula_attribute
        project_id = linking_data.project_details.id
        datasheet_id = linking_data.project_details.datasheet_id
        report_def_id = linking_data.report_definition.id
        null_uuid = zero_uuid()
        unit_instances_by_def_id: Dict[UUID, UnitInstanceCache] = {
            formula_id: list(values)
            for formula_id, values in groupby(
                linking_data.unit_instances, key=lambda x: x.formula_id
            )
            if not formula_id is None
        }

        for row in rows:
            element_id = element_attribute.get(row)
            assert isinstance(element_id, UUID)
            formula_id = formula_attribute.get(row)
            assert isinstance(element_id, UUID)

            assert (
                formula_id in unit_instances_by_def_id
            ), f"Missing formula {formula_id}"
            unit_instances = unit_instances_by_def_id[formula_id]

            for formula_instance in unit_instances:
                new_rows.append(
                    ReportRow(
                        project_id=project_id,
                        report_def_id=report_def_id,
                        group_digest="",
                        datasheet_id=datasheet_id,
                        node_id=formula_instance.node_id,
                        formula_id=formula_instance.formula_id,
                        element_id=element_id,
                        order_index=0,
                        child_reference_id=null_uuid,
                        row={**row, "formula": formula_instance.report_dict},
                    )
                )

        return new_rows

    async def _fill_datasheet_element_in_rows(
        self, report_rows: List[ReportRow], linking_data: LinkingData
    ):
        datasheet_bucket_name = (
            linking_data.report_definition.structure.datasheet_attribute.attribute_name
        )
        datasheet_id = linking_data.project_details.datasheet_id
        old_rows = (
            []
            if linking_data.old_report is None
            else chain(*[stage.rows for stage in linking_data.old_report.stages])
        )
        old_row_by_formula_cache = {
            f"{old_row.formula_id}/{old_row.node_id}": old_row for old_row in old_rows
        }

        missing_elements_for_rows: Dict[UUID, List[int]] = defaultdict(list)

        for index, report_row in enumerate(report_rows):
            formula_cache_id = f"{report_row.formula_id}/{report_row.node_id}"
            old_row = old_row_by_formula_cache.get(formula_cache_id)

            if not old_row is None:
                report_row.child_reference_id = old_row.child_reference_id
                report_row.row[datasheet_bucket_name] = old_row.row[
                    datasheet_bucket_name
                ]
            else:
                missing_elements_for_rows[report_row.element_id].append(index)

        missing_elements = await self.datasheet_element_plucker.pluck_subressources(
            DatasheetElementFilter(
                datasheet_id=datasheet_id,
                child_element_reference=zero_uuid(),
            ),
            lambda ids: DatasheetElementPluckFilter(element_def_ids=ids),
            set(missing_elements_for_rows.keys()),
        )

        assert len(missing_elements) == len(
            missing_elements_for_rows
        ), f"{len(missing_elements)} != {len(missing_elements_for_rows)}"
        for missing_element in missing_elements:
            for row_index in missing_elements_for_rows[missing_element.element_def_id]:
                report_rows[row_index].row[
                    datasheet_bucket_name
                ] = missing_element.report_dict

    def _fill_row_columns(
        self, report_rows: List[ReportRow], linking_data: LinkingData
    ):
        report_definition = linking_data.report_definition
        footprint_columns = {
            g.attribute_name
            for g in report_definition.structure.group_by
            if g.bucket_name == "columns"
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
            report_row.row["columns"] = columns

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
            columns = report_row.row["columns"]

            for column in second_pass_column:
                columns[column.name] = self._evaluate(
                    column.expression, report_row.row, rows, linking_data.injector
                )

            if columns["cost"] != 0:
                stage = report_definition.structure.stage.label.get(report_row.row)
                grouped_rows[stage].append(report_row)

        return list(chain(*grouped_rows.values()))

    def _fill_row_order(
        self, report_rows: List[ReportRow], report_definition: ReportDefinition
    ):
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

    def _build_stage_groups(
        self, report_rows: List[ReportRow], report_definition: ReportDefinition
    ) -> List[ReportGroup]:
        groups = OrderedDict()

        for report_row in report_rows:
            key = report_definition.structure.stage.label.get(report_row.row)

            if not key in groups:
                groups[key] = ReportGroup(label=key, rows=[], summary="")

            groups[key].rows.append(report_row)

        for stage_group in groups.values():
            stage_group.summary = self._evaluate(
                report_definition.structure.stage.summary.expression,
                None,
                (x.row for x in stage_group.rows),
                None,
            )

        return list(groups.values())

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

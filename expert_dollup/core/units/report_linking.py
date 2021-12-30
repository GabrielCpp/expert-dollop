import math
from typing import List, Dict, Any, Optional
from uuid import UUID
from functools import lru_cache
from collections import defaultdict
from itertools import islice, groupby
from hashlib import sha3_256
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.queries import Plucker
from expert_dollup.core.domains import *
from expert_dollup.infra.services import *
from expert_dollup.core.logits import FormulaInjector, FrozenUnit
from .expression_evaluator import ExpressionEvaluator


def round_number(number, digits, method) -> float:
    assert method == "truncate", "method is the only method supported"
    stepper = 10.0 ** digits
    return math.trunc(stepper * number) / stepper


def format_currency(number, digits, method) -> str:
    number_rounded = round_number(number, digits, method)
    return f"{number_rounded} $"


class ReportGenerationError(Exception):
    def __init__(self, message, **props):
        Exception.__init__(self, message)
        self.props = props

    def __str__(self):
        return f"{Exception.__str__(self)} {self.props}"


class IndexedCollection:
    def __init__(self, items: list):
        self.items = items


class ReportLinkingCache:
    def __init__(
        self,
        datasheet_definition_service: DatasheetDefinitionService,
        project_definition_service: ProjectDefinitionService,
        datasheet_definition_element_service: DatasheetDefinitionElementService,
        report_definition_service: ReportDefinitionService,
        label_collection_service: LabelCollectionService,
        label_service: LabelService,
    ):
        self.datasheet_definition_service = datasheet_definition_service
        self.project_definition_service = project_definition_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.report_definition_service = report_definition_service
        self.label_collection_service = label_collection_service
        self.label_service = label_service

        self._datasheet_definition: Optional[DatasheetDefinition] = None
        self._project_definition: Optional[ProjectDefinition] = None
        self._label_collections: Optional[List[LabelCollection]] = None
        self.labels: Dict[UUID, List[Label]] = {}
        self.labels_by_id: Dict[UUID, Label] = {}

    @property
    def project_definition(self) -> ProjectDefinition:
        assert not self._project_definition is None
        return self._project_definition

    @property
    def datasheet_definition(self) -> DatasheetDefinition:
        assert not self._datasheet_definition is None
        return self._datasheet_definition

    @property
    def label_collections(self) -> List[LabelCollection]:
        assert not self._label_collections is None
        return self._label_collections

    @property
    @lru_cache(maxsize=1)
    def label_collections_by_name(self) -> Dict[str, LabelCollection]:
        assert not self._label_collections is None
        return {collection.name: collection for collection in self._label_collections}

    async def load_report_project_ressources(self, project_def_id: UUID):
        self._project_definition = await self.project_definition_service.find_by_id(
            project_def_id
        )
        self._datasheet_definition = await self.datasheet_definition_service.find_by_id(
            self._project_definition.datasheet_def_id
        )
        self._label_collections = await self.label_collection_service.find_by(
            LabelCollectionFilter(datasheet_definition_id=self._datasheet_definition.id)
        )

    async def get_labels(
        self,
        label_collection: LabelCollection,
    ):
        labels = await self.label_service.find_by(
            LabelFilter(label_collection_id=label_collection.id)
        )
        self.labels[label_collection.id] = labels

        for label in labels:
            self.labels_by_id[label.id] = label

        return labels


from dataclasses import dataclass


@dataclass
class ReportCache:
    rows: List[ReportRowDict]
    warnings: List[str]


from hashlib import sha256
from expert_dollup.shared.database_services import JsonSerializer


class ReportRowCacheBuilder:
    def __init__(
        self,
        datasheet_definition_service: DatasheetDefinitionService,
        project_definition_service: ProjectDefinitionService,
        datasheet_definition_element_service: DatasheetDefinitionElementService,
        report_definition_service: ReportDefinitionService,
        label_collection_service: LabelCollectionService,
        label_service: LabelService,
        translation_plucker: Plucker[TranslationService],
        formula_plucker: Plucker[FormulaService],
    ):
        self.datasheet_definition_service = datasheet_definition_service
        self.project_definition_service = project_definition_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.report_definition_service = report_definition_service
        self.label_collection_service = label_collection_service
        self.label_service = label_service
        self.translation_plucker = translation_plucker
        self.formula_plucker = formula_plucker

    async def refresh_cache(
        self, report_definition: ReportDefinition
    ) -> List[ReportRowDict]:
        cache = ReportLinkingCache(
            self.datasheet_definition_service,
            self.project_definition_service,
            self.datasheet_definition_element_service,
            self.report_definition_service,
            self.label_collection_service,
            self.label_service,
        )

        await cache.load_report_project_ressources(report_definition.project_def_id)
        report_buckets = await self._build_from_datasheet_elements(
            report_definition, cache
        )

        for join in report_definition.structure.joins_cache:
            report_buckets = await self._join_on(report_buckets, join, cache)

        await self._join_translations(report_buckets)
        await self._join_formulas(report_buckets, report_definition)
        report_buckets = self._distinct_rows(report_buckets)

        return report_buckets

    def _distinct_rows(self, report_buckets):
        fingerprints = (
            sha256(JsonSerializer.encode(row, indent=None).encode("utf8")).hexdigest()
            for row in report_buckets
        )
        seen = {}
        filtered_bucket = [
            seen.setdefault(fingerprint, row)
            for fingerprint, row in zip(fingerprints, report_buckets)
            if not fingerprint in seen
        ]

        return filtered_bucket

    async def _build_from_datasheet_elements(
        self, report_definition: ReportDefinition, cache: ReportLinkingCache
    ):
        selection_alias = report_definition.structure.datasheet_selection_alias
        elements = await self.datasheet_definition_element_service.find_by(
            DatasheetDefinitionElementFilter(
                datasheet_def_id=cache.datasheet_definition.id
            )
        )

        report_buckets = [
            {selection_alias: element.report_dict} for element in elements
        ]

        return report_buckets

    async def _join_translations(self, report_buckets: List[Dict[str, Dict[str, Any]]]):
        ressource_ids = set()

        for report_bucket in report_buckets:
            for row in report_bucket.values():
                ressource_ids.add(row["id"])

        translations = await self.translation_plucker.plucks(
            lambda scopes: TranslationPluckFilter(scopes=scopes), ressource_ids
        )

        translations_name_by_scope: Dict[UUID, str] = {}
        for translation in translations:
            translations_name_by_scope[translation.scope] = translation.name

        for report_bucket in report_buckets:
            for bucket_name, row in report_bucket.items():
                translation_name = "<Missing translation>"
                target_id = row["id"]

                if target_id in translations_name_by_scope:
                    translation_name = translations_name_by_scope[target_id]
                else:
                    print(
                        f"Missing translation for {target_id} in bucket {bucket_name}"
                    )

                row["translation"] = translation_name

    async def _join_formulas(
        self,
        report_buckets: List[Dict[str, Dict[str, Any]]],
        report_definition: ReportDefinition,
    ):
        collection_name = report_definition.structure.formula_attribute.bucket_name
        attribute_name = report_definition.structure.formula_attribute.attribute_name
        formula_ids = set()

        for report_bucket in report_buckets:
            formula_id = report_bucket[collection_name][attribute_name]
            formula_ids.add(formula_id)

        formulas = await self.formula_plucker.plucks(
            lambda ids: FormulaPluckFilter(ids=ids), formula_ids
        )
        formulas_by_id = {formula.id: formula for formula in formulas}

        for report_bucket in report_buckets:
            formula_id = report_bucket[collection_name][attribute_name]
            formula = formulas_by_id[formula_id]
            report_bucket["formula"] = {
                "name": formula.name,
                "expression": formula.expression,
                "attached_to_type_id": formula.attached_to_type_id,
            }

    async def _join_on(
        self,
        report_buckets: List[Dict[str, Dict[str, Any]]],
        join: ReportJoin,
        cache: ReportLinkingCache,
    ):
        if not join.from_object_name in report_buckets[0]:
            raise ReportGenerationError(
                "Name not in buckets",
                name=join.from_object_name,
                avaiable_names=list(report_buckets.keys()),
            )

        if not join.from_property_name in report_buckets[0][join.from_object_name]:
            item = report_buckets[0][join.from_object_name]
            raise ReportGenerationError(
                "Property name not in bucket item",
                name=join.from_property_name,
                avaiable_names=list(item.keys()),
            )

        collections_by_names = cache.label_collections_by_name

        if not join.join_on_collection in collections_by_names:
            raise ReportGenerationError(
                "Target collection not defined",
                name=join.join_on_collection,
                avaiable_names=list(collections_by_names.keys()),
            )

        joined_collection = collections_by_names[join.join_on_collection]

        if (
            not join.join_on_attribute == "id"
            and not join.join_on_attribute in joined_collection.attributes_schema
        ):
            raise ReportGenerationError(
                "Joined property is not part of collection schema",
                name=join.join_on_attribute,
                avaiable_names=list(joined_collection.attributes_schema.keys()),
            )

        labels = await cache.get_labels(joined_collection)
        attributes_to_label = defaultdict(list)
        new_buckets: List[Dict[str, Dict[str, Any]]] = []

        for label in labels:
            a = label.get_attribute(join.join_on_attribute)
            attributes_to_label[a].append(label)

        for report_bucket in report_buckets:
            report_dict = report_bucket[join.from_object_name]
            attribute = report_dict[join.from_property_name]
            labels = self._match_attributes(attribute, attributes_to_label)

            if len(labels) == 0:
                print(f"Discarding attribute {attribute} for {join}")
                if join.allow_dicard_element:
                    continue

                raise Exception(f"Expected data {attribute} for {join}")

            report_bucket[join.alias_name] = labels[0].report_dict
            new_buckets.append(report_bucket)

            if len(labels) > 1 and join.same_cardinality:
                raise Exception(
                    f"Expected cardinality be unchanged after join on {join}"
                )

            for label in islice(labels, 1):
                new_bucket = dict(report_bucket)
                new_bucket[join.alias_name] = label.report_dict
                new_buckets.append(new_bucket)

        return new_buckets

    def _match_attributes(self, attributes, attributes_to_label):
        if isinstance(attributes, list):
            results = []

            for attribute in attributes:
                if attribute in attributes_to_label:
                    results.extend(attributes_to_label[attribute])

            return results

        if attributes in attributes_to_label:
            return attributes_to_label[attributes]

        return []


from stopwatch import Stopwatch


@dataclass
class LinkingData:
    report_definition: ReportDefinition
    project_details: ProjectDetails
    unit_instances: UnitInstanceCache
    injector: FormulaInjector


class ReportLinking:
    def __init__(
        self,
        report_def_row_cache: ObjectStorage[ReportRowsCache, ReportRowKey],
        report_row_service: ReportRowService,
        unit_instance_service: ObjectStorage[UnitInstanceCache, UnitInstanceCacheKey],
        datasheet_element_plucker: Plucker[DatasheetElementService],
        expression_evaluator: ExpressionEvaluator,
    ):
        self.report_def_row_cache = report_def_row_cache
        self.unit_instance_service = unit_instance_service
        self.report_row_service = report_row_service
        self.datasheet_element_plucker = datasheet_element_plucker
        self.expression_evaluator = expression_evaluator

    async def link_report(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
    ) -> List[ReportRow]:
        from tests.fixtures import dump_to_file

        linking_data = await self._preload_data(report_definition, project_details)

        with Stopwatch("self.report_def_row_cache.load") as w:
            rows = await self.report_def_row_cache.load(
                ReportRowKey(
                    project_def_id=report_definition.project_def_id,
                    report_definition_id=report_definition.id,
                )
            )
            print(w.report())

        dump_to_file(rows)

        with Stopwatch("self._join_row_cache_with_unit_instances") as w:
            new_rows = await self._join_row_cache_with_unit_instances(
                rows, linking_data
            )

        dump_to_file(new_rows)

        with Stopwatch("self._fill_datasheet_element_in_rows.load") as w:
            await self._fill_datasheet_element_in_rows(new_rows, linking_data)
            print(w.report())

        grouped_rows = self._fill_row_columns(new_rows, linking_data)

        dump_to_file(grouped_rows)
        # self._fill_row_order(grouped_rows, report_definition)

        return grouped_rows

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

        return LinkingData(
            report_definition=report_definition,
            project_details=project_details,
            unit_instances=unit_instances,
            injector=injector,
        )

    async def _join_row_cache_with_unit_instances(
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
            element_id = UUID(element_attribute.get(row))
            formula_id = UUID(formula_attribute.get(row))

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
        project_id = linking_data.project_details.id
        datasheet_id = linking_data.project_details.datasheet_id
        old_rows = await self.report_row_service.find_by(
            ReportRowFilter(project_id=project_id)
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
                report_row.row["datasheet_element"] = old_row["datasheet_element"]
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
                    "datasheet_element"
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

            if columns["cost"] != "0.0 $":
                stage = report_definition.structure.stage_attribute.get(report_row.row)
                grouped_rows[stage].append(columns)

        return grouped_rows

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

    def _evaluate(self, expression, row, rows_group, injector):
        try:
            return self.expression_evaluator.evaluate(
                expression,
                {
                    "row": row,
                    "rows": rows_group,
                    "round_number": round_number,
                    "format_currency": format_currency,
                    "sum": sum,
                    "injector": injector,
                },
            )
        except Exception as e:
            raise Exception(f"Failed to calculate {expression}") from e

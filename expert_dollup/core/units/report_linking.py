from typing import List, Dict, Any, Optional, Set
from expert_dollup.core.domains import *
from expert_dollup.core.queries import Plucker
from expert_dollup.infra.services import *
from uuid import UUID
from functools import lru_cache
from collections import defaultdict
from itertools import islice
from hashlib import sha3_256


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

    async def get_datasheet_definition_elements(self):
        return await self.datasheet_definition_element_service.find_by(
            DatasheetDefinitionElementFilter(
                datasheet_def_id=self.datasheet_definition.id
            )
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
        self.datasheet_definition_element = datasheet_definition_element_service
        self.report_definition_service = report_definition_service
        self.label_collection_service = label_collection_service
        self.label_service = label_service
        self.translation_plucker = translation_plucker
        self.formula_plucker = formula_plucker

    async def refresh_cache(
        self, report_definition: ReportDefinition
    ) -> List[Dict[str, Dict[str, Any]]]:
        cache = ReportLinkingCache(
            self.datasheet_definition_service,
            self.project_definition_service,
            self.datasheet_definition_element,
            self.report_definition_service,
            self.label_collection_service,
            self.label_service,
        )

        await cache.load_report_project_ressources(report_definition.project_def_id)
        elements = await cache.get_datasheet_definition_elements()

        selection_alias = report_definition.structure.datasheet_selection_alias
        report_buckets = [
            {selection_alias: element.report_dict} for element in elements
        ]

        for join in report_definition.structure.joins_cache:
            await self._join_on(report_buckets, join, cache)

        await self._join_translations(report_buckets)
        await self._join_formulas(report_buckets, cache)

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
            for row in report_bucket.values():
                row["translation"] = translations_name_by_scope[row["id"]]

    async def _join_formulas(
        self,
        report_buckets: List[Dict[str, Dict[str, Any]]],
        cache: ReportLinkingCache,
    ):
        formulas_aggregates = []

        for label_collection in cache.label_collections:
            for name, schema in label_collection.attributes_schema.items():
                if isinstance(schema, FormulaAggregate):
                    formulas_aggregates.append((label_collection.name, name))

        if len(formulas_aggregates) == 0:
            raise Exception("One formula aggregate required")

        if len(formulas_aggregates) > 1:
            raise Exception("Only formula aggregate accepted")

        collection_name, attribute_name = formulas_aggregates[0]
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
                raise Exception(f"Expected data {attribute}")

            report_bucket[join.alias_name] = labels[0].report_dict

            for label in islice(labels, 1):
                new_bucket = dict(report_bucket)
                new_bucket[join.alias_name] = label.report_dict
                new_buckets.append(new_bucket)

        report_buckets.extend(new_buckets)

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


class ReportLinking:
    def __init__(
        self,
        formula_cache_plucker: Plucker[FormulaCacheService],
        report_row_service: ReportRowService,
        datasheet_element_plucker: Plucker[DatasheetElementService],
    ):
        self.formula_cache_plucker = formula_cache_plucker
        self.report_row_service = report_row_service
        self.datasheet_element_plucker = datasheet_element_plucker

    async def link_report(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
    ) -> List[ReportRow]:
        rows = await self.report_cache.find_by(
            ReportCacheFilter(report_def_id=report_definition.id)
        )

        formula_attribute = report_definition.structure.formula_attribute
        formula_ids = {formula_attribute.get(row) for row in rows}

        formulas_result = await self.formula_cache_plucker.pluck_subressources(
            FormulaCachedResultFilter(project_id=project_details.id),
            lambda ids: FormulaCachePluckFilter(formula_ids=ids),
            formula_ids,
        )

        formulas_result_by_formula_id: Dict[
            UUID, List[FormulaCachedResult]
        ] = defaultdict(list)
        for formula_result in formulas_result:
            formulas_result_by_formula_id[formula_result.formula_id].append(
                formula_result
            )

        element_attribute = report_definition.structure.datasheet_attribute
        new_rows: List[ReportRow] = []
        for row in rows:
            element_id = element_attribute.get(row)
            formula_id = formula_attribute.get(row)
            cached_formulas = formulas_result_by_formula_id[formula_id]

            for cached_formula in cached_formulas:
                new_row = dict(row)
                new_row["formula"] = cached_formula.report_dict
                group_id = "/".join(
                    attribute_bucket.get(row)
                    for attribute_bucket in report_definition.structure.group_by
                )

                new_rows.append(
                    ReportRow(
                        project_id=project_details.id,
                        report_def_id=report_definition.id,
                        group_digest=sha3_256(group_id),
                        datasheet_id=project_details.datasheet_id,
                        node_id=cached_formula.node_id,
                        formula_id=cached_formula.formula_id,
                        element_id=element_id,
                        order_index=0,
                        child_reference_id=zero_uuid(),
                        row=row,
                    )
                )

        old_rows = await self.report_row_service.find_by(
            ReportRowFilter(project_id=project_details.id)
        )

        old_row_by_formula_cache = {
            f"{old_row.formula_id}/{old_row.node_id}": old_row for old_row in old_rows
        }

        missing_elements_for_rows: Dict[UUID, List[int]] = defaultdict(list)

        for index, new_row in enumerate(new_rows):
            formula_cache_id = f"{new_row.formula_id}/{new_row.node_id}"
            old_row = old_row_by_formula_cache.get(formula_cache_id)

            if not old_row is None:
                new_row.child_reference_id = old_row.child_reference_id
                new_row["datasheet_element"] = old_row["datasheet_element"]
            else:
                missing_elements_for_rows[new_row.element_id].append(index)

        missing_elements = await self.datasheet_element_plucker.pluck_subressources(
            DatasheetElementFilter(
                datasheet_id=project_details.datasheet_id,
                child_element_reference=zero_uuid(),
            ),
            lambda ids: DatasheetElementPluckFilter(element_ids=ids),
            missing_elements_for_rows.keys(),
        )

        for missing_element in missing_elements:
            for row_index in missing_elements_for_rows[missing_element.element_id]:
                new_rows[row_index]["datasheet_element"] = missing_element.report_dict

        for new_row in new_rows:
            columns = {}
            new_row["columns"] = columns

            for column in report_definition.structure.columns:
                columns[column.name] = self.evaluate(column.expression, new_row)

        def get_row_order_tuple(row: ReportRow) -> list:
            ordering = []
            for attribute_bucket in report_definition.structure.order_by:
                value = attribute_bucket.get(row)
                ordering.append(value)

            return ordering

        new_rows.sort(key=get_row_order_tuple)

        return new_rows

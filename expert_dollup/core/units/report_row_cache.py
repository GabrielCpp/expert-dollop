from asyncio import gather
from typing import List, Dict, Any
from uuid import UUID
from collections import defaultdict
from itertools import islice
from dataclasses import dataclass
from hashlib import sha256
from expert_dollup.shared.database_services import JsonSerializer, CollectionService
from expert_dollup.core.queries import Plucker
from expert_dollup.core.domains import *
from expert_dollup.core.exceptions import ReportGenerationError, RessourceNotFound
from expert_dollup.core.object_storage import ObjectStorage


@dataclass
class ReportCache:
    warnings: List[str]
    report_definition: ReportDefinition
    project_definition: ProjectDefinition
    label_collections: List[LabelCollection]
    labels_by_collection_id: Dict[UUID, List[Label]]
    labels_by_id: Dict[UUID, Label]
    label_collections_by_name: Dict[str, LabelCollection]


class ReportRowCache:
    def __init__(
        self,
        project_definition_service: CollectionService[ProjectDefinition],
        datasheet_definition_element_service: CollectionService[
            DatasheetDefinitionElement
        ],
        label_collection_service: CollectionService[LabelCollection],
        label_service: CollectionService[Label],
        formula_plucker: Plucker[Formula],
        report_def_row_cache: ObjectStorage[ReportRowsCache, ReportRowKey],
    ):
        self.project_definition_service = project_definition_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.label_collection_service = label_collection_service
        self.label_service = label_service
        self.formula_plucker = formula_plucker
        self.report_def_row_cache = report_def_row_cache

    async def refresh_cache(
        self, report_definition: ReportDefinition
    ) -> ReportRowsCache:
        key = ReportRowKey(
            project_def_id=report_definition.project_def_id,
            report_definition_id=report_definition.id,
        )

        try:
            return await self.report_def_row_cache.load(key)
        except RessourceNotFound:
            rows = await self.build_cache(report_definition)
            await self.report_def_row_cache.save(key, rows)
            return rows

    async def build_cache(
        self, report_definition: ReportDefinition
    ) -> List[ReportRowDict]:
        cache = await self._build_report_cache(report_definition)
        report_buckets = await self._build_from_datasheet_elements(cache)

        for join in report_definition.structure.joins_cache:
            report_buckets = self._join_on(report_buckets, join, cache)

        await self._join_formulas(report_buckets, report_definition)
        report_buckets = self._distinct_rows(report_buckets)

        return report_buckets

    async def _build_report_cache(
        self, report_definition: ReportDefinition
    ) -> ReportCache:
        project_definition = await self.project_definition_service.find_by_id(
            report_definition.project_def_id
        )

        project_definition = await self.project_definition_service.find_by_id(
            project_definition.project_definition_id
        )

        label_collections = await self.label_collection_service.find_by(
            LabelCollectionFilter(project_definition_id=project_definition.id)
        )

        collections_labels = await gather(
            *[
                self.label_service.find_by(
                    LabelFilter(label_collection_id=label_collection.id)
                )
                for label_collection in label_collections
            ]
        )

        labels_by_collection_id: Dict[UUID, List[Label]] = {}
        labels_by_id: Dict[UUID, Label] = {}

        for label_collection, labels in zip(label_collections, collections_labels):
            labels_by_collection_id[label_collection.id] = labels

            for label in labels:
                assert label.label_collection_id == label_collection.id
                labels_by_id[label.id] = label

        return ReportCache(
            warnings=[],
            report_definition=report_definition,
            project_definition=project_definition,
            label_collections=label_collections,
            labels_by_collection_id=labels_by_collection_id,
            labels_by_id=labels_by_id,
            label_collections_by_name={
                collection.name: collection for collection in label_collections
            },
        )

    def _distinct_rows(self, report_buckets):
        fingerprints = (
            sha256(JsonSerializer.encode(row)).hexdigest() for row in report_buckets
        )
        seen = {}
        filtered_bucket = [
            seen.setdefault(fingerprint, row)
            for fingerprint, row in zip(fingerprints, report_buckets)
            if not fingerprint in seen
        ]

        return filtered_bucket

    async def _build_from_datasheet_elements(
        self, cache: ReportCache
    ) -> ReportRowsCache:
        selection_alias = cache.report_definition.structure.datasheet_selection_alias
        elements = await self.datasheet_definition_element_service.find_by(
            DatasheetDefinitionElementFilter(
                project_definition_id=cache.project_definition.id
            )
        )

        report_buckets: ReportCache = [
            {selection_alias: element.report_dict} for element in elements
        ]

        return report_buckets

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
            report_bucket["formula"] = formula.report_dict

    def _join_on(
        self,
        report_buckets: List[Dict[str, Dict[str, Any]]],
        join: ReportJoin,
        cache: ReportCache,
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

        labels = cache.labels_by_collection_id[joined_collection.id]
        new_buckets: ReportRowsCache = []
        attributes_to_label = defaultdict(list)
        seen = set()

        for label in labels:
            a = label.get_attribute(join.join_on_attribute)
            attributes_to_label[a].append(label)

        for report_bucket in report_buckets:
            report_dict = report_bucket[join.from_object_name]
            attribute = report_dict[join.from_property_name]

            if attribute in attributes_to_label:
                seen.add(attribute)
                matchs = attributes_to_label[attribute]
            else:
                cache.warnings.append(f"Discarding attribute {attribute} for {join}")
                if join.allow_dicard_element:
                    continue

                raise Exception(f"Expected data {attribute} for {join}")

            report_bucket[join.alias_name] = matchs[0].report_dict
            new_buckets.append(report_bucket)

            if len(matchs) > 1 and join.same_cardinality:
                raise Exception(
                    f"Expected cardinality be unchanged after join on {join}"
                )

            for label in islice(matchs, 1, len(matchs)):
                new_bucket = dict(report_bucket)
                new_bucket[join.alias_name] = label.report_dict
                new_buckets.append(new_bucket)

        """
        
        assert len(seen) == len(
            attributes_to_label
        ), f"Unused {len(attributes_to_label) - len(seen)} labels for collection {joined_collection.name}"
        """
        return new_buckets

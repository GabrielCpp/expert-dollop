from asyncio import gather
from json import dump
from typing import List, Dict, Any
from uuid import UUID
from collections import defaultdict
from itertools import islice
from dataclasses import dataclass
from hashlib import sha256
from expert_dollup.shared.database_services import JsonSerializer
from expert_dollup.core.queries import Plucker
from expert_dollup.core.domains import *
from expert_dollup.infra.services import *
from expert_dollup.core.exceptions import ReportGenerationError


@dataclass
class ReportCache:
    warnings: List[str]
    report_definition: ReportDefinition
    project_definition: ProjectDefinition
    datasheet_definition: DatasheetDefinition
    label_collections: List[LabelCollection]
    labels_by_collection_id: Dict[UUID, List[Label]]
    labels_by_id: Dict[UUID, Label]
    label_collections_by_name: Dict[str, LabelCollection]


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
        cache = await self._build_report_cache(report_definition)
        report_buckets = await self._build_from_datasheet_elements(cache)

        for join in report_definition.structure.joins_cache:
            report_buckets = await self._join_on(report_buckets, join, cache)

        await self._join_translations(report_buckets)
        await self._join_formulas(report_buckets, report_definition)
        report_buckets = self._distinct_rows(report_buckets)

        return report_buckets

    async def _build_report_cache(
        self, report_definition: ReportDefinition
    ) -> ReportCache:
        project_definition = await self.project_definition_service.find_by_id(
            report_definition.project_def_id
        )

        datasheet_definition = await self.datasheet_definition_service.find_by_id(
            project_definition.datasheet_def_id
        )

        label_collections = await self.label_collection_service.find_by(
            LabelCollectionFilter(datasheet_definition_id=datasheet_definition.id)
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
            datasheet_definition=datasheet_definition,
            label_collections=label_collections,
            labels_by_collection_id=labels_by_collection_id,
            labels_by_id=labels_by_id,
            label_collections_by_name={
                collection.name: collection for collection in label_collections
            },
        )

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
        self, cache: ReportCache
    ) -> ReportRowsCache:
        selection_alias = cache.report_definition.structure.datasheet_selection_alias
        elements = await self.datasheet_definition_element_service.find_by(
            DatasheetDefinitionElementFilter(
                datasheet_def_id=cache.datasheet_definition.id
            )
        )

        report_buckets: ReportCache = [
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
            matchs = self._match_attributes(attribute, attributes_to_label, seen)

            if len(matchs) == 0:
                print(f"Discarding attribute {attribute} for {join}")
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

    def _match_attributes(self, attributes, attributes_to_label, seen) -> List[Label]:
        if isinstance(attributes, list):
            results = []

            for attribute in attributes:
                if attribute in attributes_to_label:
                    results.extend(attributes_to_label[attribute])
                    seen.add(attribute)

            return results

        if attributes in attributes_to_label:
            seen.add(attributes)
            return attributes_to_label[attributes]

        return []

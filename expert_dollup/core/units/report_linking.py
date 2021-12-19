from typing import List, Dict, Any, Optional, Set
from expert_dollup.core.domains import *
from expert_dollup.core.queries import Plucker
from expert_dollup.infra.services import *
from uuid import UUID
from functools import lru_cache
from collections import defaultdict
from itertools import islice


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
        label_plucker: Plucker[LabelService],
    ):
        self.datasheet_definition_service = datasheet_definition_service
        self.project_definition_service = project_definition_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.report_definition_service = report_definition_service
        self.label_collection_service = label_collection_service
        self.label_service = label_service
        self.label_plucker = label_plucker

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


class ReportLinking:
    def __init__(
        self,
        datasheet_definition_service: DatasheetDefinitionService,
        project_definition_service: ProjectDefinitionService,
        datasheet_definition_element_service: DatasheetDefinitionElementService,
        report_definition_service: ReportDefinitionService,
        label_collection_service: LabelCollectionService,
        label_service: LabelService,
        label_plucker: Plucker[LabelService],
    ):
        self.datasheet_definition_service = datasheet_definition_service
        self.project_definition_service = project_definition_service
        self.datasheet_definition_element = datasheet_definition_element_service
        self.report_definition_service = report_definition_service
        self.label_collection_service = label_collection_service
        self.label_service = label_service
        self.label_plucker = label_plucker

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
            self.label_plucker,
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
        formula_ids = set()

        # Join translation
        # Join formula def

        return report_buckets

    def _join_translations(self, report_buckets: List[Dict[str, Dict[str, Any]]]):
        ressource_ids = set()

        for report_bucket in report_buckets:
            for row in report_bucket.values():
                ressource_ids.add(row["id"])

        translations = self.translation_plucker.plucks(
            TranslationPluckFilter(scopes=ressource_ids)
        )

        translations_by_scope = defaultdict(dict)
        for translation in translations:
            translations_by_scope[translation.scope][translation.locale] = translation

        for report_bucket in report_buckets:
            for row in report_bucket.values():
                row["translations"] = translations_by_scope[row["id"]]

    def link_report(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
        locale: str,
    ):
        # project_formula_cache 1 def + project -> instance
        # datasheet 1 def + datasheet -> instance
        # project_report_datasheet_rule -> element instance -> maybe
        # run column rendering on each row
        # run group by
        # run orderby
        pass

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

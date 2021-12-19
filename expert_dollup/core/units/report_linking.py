from typing import List, Dict, Any, Set
from dataclasses import dataclass, field
from expert_dollup.core.domains import *
from expert_dollup.core.queries import Plucker
from expert_dollup.infra.services import (
    ReportDefinitionService,
    LabelCollectionService,
    LabelService,
)
from uuid import UUID


@dataclass
class ReportLinkingCache:
    label_collections: Dict[str, List[LabelCollection]] = field(default_factory=dict)
    labels: Dict[UUID, List[Label]] = field(default_factory=dict)
    labels_by_id: Dict[UUID, Label] = field(default_factory=dict)

    async def get_labels(
        self,
        label_collection_service: LabelCollectionService,
        label_service: LabelService,
        collection_name: str,
    ):
        if collection_name in self.label_collections:
            label_collection = self.label_collections[collection_name]
            labels = self.labels[label_collection.id]
            return labels

        label_collection = await label_collection_service.find_one_by(
            LabelCollectionFilter(name=collection_name)
        )
        self.label_collections[label_collection.name] = label_collection

        labels = await label_service.find_by(
            LabelFilter(label_collection_id=label_collection.id)
        )
        self.labels[label_collection.id] = labels

        for label in labels:
            self.labels_by_id[label.id] = label

        return labels

    async def get_aggregates(
        self, label_plucker: Plucker[LabelService], ids: Set[UUID]
    ) -> Dict[UUID, Label]:
        labels = {id: self.labels_by_id[id] for id in ids if id in self.labels_by_id}
        remaining_ids = ids - set(labels.keys())
        remaining_labels = await label_plucker.plucks(
            lambda ids: LabelPluckFilter(ids=ids), remaining_ids
        )

        for remaining_label in remaining_labels:
            self.labels_by_id[remaining_label.id] = remaining_label
            labels[remaining_label.id] = remaining_label

        return labels


class ReportLinking:
    def __init__(
        self,
        report_definition_service: ReportDefinitionService,
        label_collection_service: LabelCollectionService,
        label_service: LabelService,
        label_plucker: Plucker[LabelService],
    ):
        self.report_definition_service = report_definition_service
        self.label_collection_service = label_collection_service
        self.label_service = label_service
        self.label_plucker = label_plucker

    async def refresh_cache(self, report_definition: ReportDefinition):
        cache = ReportLinkingCache()
        initial_select = report_definition.structure.initial_selection
        report_buckets = self._initial_select(initial_select, cache)

        for join in report_definition.structure.joins:
            await self._join_on(report_buckets, join, cache)

    def link_report(
        self,
        report_definition: ReportDefinition,
        project_details: ProjectDetails,
        locale: str,
    ):
        pass

    async def _initial_select(
        self,
        initial_select: ReportInitialSelection,
        cache: ReportLinkingCache,
    ) -> List[Dict[str, Dict[str, Any]]]:
        report_buckets: List[Dict[str, Dict[str, Any]]] = []

        if initial_select.join_type == JoinType.LABEL_PROPERTY:
            labels = await cache.get_labels(
                self.label_collection_service,
                self.label_service,
                ReportLinkingCache.to_object_name,
            )

            properties_iter = (
                label.properties[initial_select.from_property_name] for label in labels
            )
            properties = (
                set(properties_iter)
                if initial_select.distinct
                else list(properties_iter)
            )

            for label_property in properties:
                report_buckets.append({initial_select.alias_name: label_property})

        return report_buckets

    async def _join_on(
        self,
        report_buckets: List[Dict[str, Dict[str, Any]]],
        join: ReportJoin,
        cache: ReportLinkingCache,
    ):

        if join.join_type == JoinType.LABEL_PROPERTY:
            labels = await cache.get_labels(
                self.label_collection_service, self.label_service, join.to_object_name
            )
            self._inner_join_on_properties(join, report_buckets, labels)

        if join.join_type == JoinType.LABEL_AGGREGATE:
            labels = await cache.get_labels(
                self.label_collection_service, self.label_service, join.to_object_name
            )
            await self._inner_join_on_aggregates(join, report_buckets, labels, cache)

    def _inner_join_on_buckets(
        self,
        join: ReportJoin,
        report_buckets: List[Dict[str, Dict[str, Any]]],
        other_buckets: List[Dict[str, Dict[str, Any]]],
    ):
        for report_bucket in report_buckets:
            for other_report_bucket in other_buckets:
                bucket_value = report_bucket[join.from_object_name][
                    join.from_property_name
                ]
                other_bucket_value = other_report_bucket[join.to_object_name][
                    join.to_property_name
                ]

                if bucket_value == other_bucket_value:
                    report_bucket[join.alias_name] = other_bucket_value

    def _inner_join_on_properties(
        self,
        join: ReportJoin,
        report_buckets: List[Dict[str, Dict[str, Any]]],
        labels: List[Label],
    ):
        for report_bucket in report_buckets:
            property_value = label.properties[join.to_property_name]
            bucket_value = report_bucket[join.from_object_name][join.from_property_name]

            for label in labels:
                if bucket_value == property_value:
                    report_bucket[join.alias_name] = property_value

    async def _inner_join_on_aggregates(
        self,
        join: ReportJoin,
        report_buckets: List[Dict[str, Dict[str, Any]]],
        labels: List[Label],
        cache: ReportLinkingCache,
    ):
        aggregate_ids: Set[UUID] = set()

        for report_bucket in report_buckets:
            aggregate_id = label.aggregates[join.to_property_name]
            bucket_value = report_bucket[join.from_object_name][join.from_property_name]

            for label in labels:
                if bucket_value == aggregate_id:
                    report_bucket[join.alias_name] = aggregate_id
                    aggregate_ids.add(aggregate_id)

        aggregates_by_id = await cache.get_aggregates(self.label_plucker, aggregate_ids)

        for report_bucket in report_buckets:
            aggregate_id = report_bucket[join.alias_name]
            aggregate = aggregates_by_id[aggregate_id]

            collpased_aggregate = {}
            collpased_aggregate.update(aggregate.properties)
            collpased_aggregate.update(aggregate.aggregates)

            report_bucket[join.alias_name] = collpased_aggregate

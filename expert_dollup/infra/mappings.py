from typing import List
from uuid import UUID
from expert_dollup.shared.starlette_injection import Clock
from expert_dollup.shared.database_services import *
from expert_dollup.shared.automapping import (
    Mapper,
    map_dict_keys,
    RevervibleUnionMapping,
)
from expert_dollup.core.utils import *
from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.infra.ressource_auth_db import *
from expert_dollup.infra.expert_dollup_storage import *
from expert_dollup.core.domains import *
from expert_dollup.core.units.evaluator import Unit

from datetime import datetime


def build_cursor(d: datetime, *args: str) -> str:
    return "_".join([d.isoformat(sep="T", timespec="auto"), *args])


primitive_with_none_union_dao_mappings = RevervibleUnionMapping(
    PrimitiveWithNoneUnionDao,
    PrimitiveWithNoneUnion,
    {
        BoolFieldValueDao: bool,
        IntFieldValueDao: int,
        StringFieldValueDao: str,
        DecimalFieldValueDao: Decimal,
        type(None): type(None),
    },
)

primitive_union_dao_mappings = RevervibleUnionMapping(
    PrimitiveUnionDao,
    PrimitiveUnion,
    {
        BoolFieldValueDao: bool,
        IntFieldValueDao: int,
        StringFieldValueDao: str,
        DecimalFieldValueDao: Decimal,
    },
)

primitive_with_reference_union_dao_mappings = RevervibleUnionMapping(
    PrimitiveUnionDao,
    PrimitiveUnion,
    {
        BoolFieldValueDao: bool,
        IntFieldValueDao: int,
        StringFieldValueDao: str,
        DecimalFieldValueDao: Decimal,
        ReferenceIdDao: UUID,
    },
)

field_details_to_domain_map = RevervibleUnionMapping(
    FieldDetailsUnionDao,
    FieldDetailsUnion,
    {
        IntFieldConfigDao: IntFieldConfig,
        DecimalFieldConfigDao: DecimalFieldConfig,
        StringFieldConfigDao: StringFieldConfig,
        BoolFieldConfigDao: BoolFieldConfig,
        StaticChoiceFieldConfigDao: StaticChoiceFieldConfig,
        CollapsibleContainerFieldConfigDao: CollapsibleContainerFieldConfig,
        StaticNumberFieldConfigDao: StaticNumberFieldConfig,
        AggregateReferenceConfigDao: AggregateReferenceConfig,
        NodeReferenceConfigDao: NodeReferenceConfig,
        type(None): type(None),
    },
)


def get_display_query_id(global_id: UUID, path: List[UUID]) -> UUID:
    display_query_internal_id: UUID = global_id
    level = len(path)

    if level >= SECTION_LEVEL and level <= FORM_LEVEL:
        display_query_internal_id = path[ROOT_LEVEL]
    elif level > FORM_LEVEL:
        display_query_internal_id = path[FORM_LEVEL]

    return display_query_internal_id


def map_project_definition_from_dao(
    src: ProjectDefinitionDao, mapper: Mapper
) -> ProjectDefinition:
    return ProjectDefinition(
        id=src.id,
        name=src.name,
        creation_date_utc=src.creation_date_utc,
    )


def map_project_definition_to_dao(
    src: ProjectDefinition, mapper: Mapper
) -> ProjectDefinitionDao:
    return ProjectDefinitionDao(
        id=src.id,
        name=src.name,
        creation_date_utc=src.creation_date_utc,
    )


def map_int_field_config_to_dao(
    src: IntFieldConfig, mapper: Mapper
) -> IntFieldConfigDao:
    return IntFieldConfigDao(unit=src.unit, integer=src.default_value)


def map_int_field_config_from_dao(
    src: IntFieldConfigDao, mapper: Mapper
) -> IntFieldConfig:
    return IntFieldConfig(unit=src.unit, default_value=src.integer)


def map_decimal_field_config_to_dao(
    src: DecimalFieldConfig, mapper: Mapper
) -> DecimalFieldConfigDao:
    return DecimalFieldConfigDao(
        unit=src.unit, precision=src.precision, numeric=src.default_value
    )


def map_decimal_field_config_from_dao(
    src: DecimalFieldConfigDao, mapper: Mapper
) -> DecimalFieldConfig:
    return DecimalFieldConfig(
        unit=src.unit, precision=src.precision, default_value=src.numeric
    )


def map_string_field_config_to_dao(
    src: StringFieldConfig, mapper: Mapper
) -> StringFieldConfigDao:
    return StringFieldConfigDao(transforms=src.transforms, text=src.default_value)


def map_string_field_config_from_dao(
    src: StringFieldConfigDao, mapper: Mapper
) -> StringFieldConfig:
    return StringFieldConfig(transforms=src.transforms, default_value=src.text)


def map_bool_field_config_to_dao(
    src: BoolFieldConfig, mapper: Mapper
) -> BoolFieldConfigDao:
    return BoolFieldConfigDao(enabled=src.default_value)


def map_bool_field_config_from_dao(
    src: BoolFieldConfigDao, mapper: Mapper
) -> BoolFieldConfig:
    return BoolFieldConfig(default_value=src.enabled)


def map_static_choice_field_config_to_dao(
    src: StaticChoiceFieldConfig, mapper: Mapper
) -> StaticChoiceFieldConfigDao:
    return StaticChoiceFieldConfigDao(
        options=[
            StaticChoiceOptionDao(
                id=option.id,
                label=option.label,
                help_text=option.help_text,
            )
            for option in src.options
        ],
        selected=src.default_value,
    )


def map_static_choice_field_config_from_dao(
    src: StaticChoiceFieldConfigDao, mapper: Mapper
) -> StaticChoiceFieldConfig:
    return StaticChoiceFieldConfig(
        options=[
            StaticChoiceOption(
                id=option.id,
                label=option.label,
                help_text=option.help_text,
            )
            for option in src.options
        ],
        default_value=src.selected,
    )


def map_collapsible_container_field_config_to_dao(
    src: CollapsibleContainerFieldConfig, mapper: Mapper
) -> CollapsibleContainerFieldConfigDao:
    return CollapsibleContainerFieldConfigDao(is_collapsible=src.is_collapsible)


def map_collapsible_container_field_config_from_dao(
    src: CollapsibleContainerFieldConfigDao, mapper: Mapper
) -> CollapsibleContainerFieldConfig:
    return CollapsibleContainerFieldConfig(is_collapsible=src.is_collapsible)


def map_static_number_field_config_to_dao(
    src: StaticNumberFieldConfig, mapper: Mapper
) -> StaticNumberFieldConfigDao:
    return StaticNumberFieldConfigDao(
        pass_to_translation=src.pass_to_translation,
        precision=src.precision,
        unit=src.unit,
    )


def map_static_number_field_config_from_dao(
    src: StaticNumberFieldConfigDao, mapper: Mapper
) -> StaticNumberFieldConfig:
    return StaticNumberFieldConfig(
        pass_to_translation=src.pass_to_translation,
        precision=src.precision,
        unit=src.unit,
    )


def map_aggregate_reference_config_to_dao(
    src: AggregateReferenceConfig, mapper: Mapper
) -> AggregateReferenceConfigDao:
    return AggregateReferenceConfigDao(from_collection=src.from_collection)


def map_aggregate_reference_config_from_dao(
    src: AggregateReferenceConfigDao, mapper: Mapper
) -> AggregateReferenceConfig:
    return AggregateReferenceConfig(from_collection=src.from_collection)


def map_node_reference_config_to_dao(
    src: NodeReferenceConfig, mapper: Mapper
) -> NodeReferenceConfigDao:
    return NodeReferenceConfigDao(node_type=str(src.node_type))


def map_node_reference_config_from_dao(
    src: NodeReferenceConfigDao, mapper: Mapper
) -> NodeReferenceConfig:
    return NodeReferenceConfig(node_type=NodeType(src.node_type))


def map_project_definition_node_to_dao(
    src: ProjectDefinitionNode, mapper: Mapper
) -> ProjectDefinitionNodeDao:
    display_query_internal_id = get_display_query_id(
        src.project_definition_id, src.path
    )

    return ProjectDefinitionNodeDao(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        path=join_uuid_path(src.path),
        display_query_internal_id=display_query_internal_id,
        level=len(src.path),
        creation_date_utc=src.creation_date_utc,
        config=DefinitionNodeConfigDao(
            is_collection=src.is_collection,
            instanciate_by_default=src.instanciate_by_default,
            ordinal=src.ordinal,
            translations=TranslationConfigDao(
                help_text_name=src.translations.help_text_name,
                label=src.translations.label,
            ),
            triggers=[
                TriggerDao(
                    action=trigger.action.value,
                    target_type_id=trigger.target_type_id,
                    params=trigger.params,
                )
                for trigger in src.triggers
            ],
            meta=NodeMetaConfigDao(is_visible=src.meta.is_visible),
            field_details=mapper.map(
                src.field_details, field_details_to_domain_map.to_origin
            ),
        ),
    )


def map_project_definition_node_from_dao(
    src: ProjectDefinitionNodeDao, mapper: Mapper
) -> ProjectDefinitionNode:
    return ProjectDefinitionNode(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        is_collection=src.config.is_collection,
        instanciate_by_default=src.config.instanciate_by_default,
        ordinal=src.config.ordinal,
        translations=TranslationConfig(
            help_text_name=src.config.translations.help_text_name,
            label=src.config.translations.label,
        ),
        triggers=[
            Trigger(
                action=TriggerAction[trigger.action],
                target_type_id=trigger.target_type_id,
                params=trigger.params,
            )
            for trigger in src.config.triggers
        ],
        meta=NodeMetaConfig(is_visible=src.config.meta.is_visible),
        field_details=mapper.map(
            src.config.field_details, field_details_to_domain_map.from_origin
        ),
        path=split_uuid_path(src.path),
        creation_date_utc=src.creation_date_utc,
    )


def map_project_from_dao(src: ProjectDao, mapper: Mapper) -> ProjectDetails:
    return ProjectDetails(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_definition_id=src.project_definition_id,
        datasheet_id=src.datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_project_to_dao(src: ProjectDetails, mapper: Mapper) -> ProjectDao:
    return ProjectDao(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_definition_id=src.project_definition_id,
        datasheet_id=src.datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_project_node_to_dao(src: ProjectNode, mapper: Mapper) -> ProjectNodeDao:
    display_query_internal_id = get_display_query_id(src.project_id, src.path)

    return ProjectNodeDao(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        type_name=src.type_name,
        path=join_uuid_path(src.path),
        value=mapper.map(src.value, primitive_with_none_union_dao_mappings.to_origin),
        label=src.label,
        type_path=join_uuid_path(src.type_path),
        level=len(src.path),
        display_query_internal_id=display_query_internal_id,
    )


def map_project_node_from_dao(src: ProjectNodeDao, mapper: Mapper) -> ProjectNode:
    return ProjectNode(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        type_name=src.type_name,
        path=split_uuid_path(src.path),
        type_path=split_uuid_path(src.type_path),
        value=mapper.map(src.value, primitive_with_none_union_dao_mappings.from_origin),
        label=src.label,
    )


def map_project_node_meta_to_dao(
    src: ProjectNodeMeta, mapper: Mapper
) -> ProjectNodeMetaDao:
    return ProjectNodeMetaDao(
        project_id=src.project_id,
        type_id=src.type_id,
        definition=mapper.map(src.definition, ProjectDefinitionNodeDao),
        state=mapper.map(src.state, ProjectNodeMetaStateDao),
        display_query_internal_id=get_display_query_id(
            src.project_id, src.definition.path
        ),
    )


def map_project_node_meta_from_dao(
    src: ProjectNodeMetaDao, mapper: Mapper
) -> ProjectNodeMeta:
    return ProjectNodeMeta(
        project_id=src.project_id,
        type_id=src.type_id,
        state=mapper.map(src.state, ProjectNodeMetaState),
        definition=mapper.map(src.definition, ProjectDefinitionNode),
    )


def map_project_node_meta_state_to_dao(
    src: ProjectNodeMetaState, mapper: Mapper
) -> ProjectNodeMetaStateDao:
    return ProjectNodeMetaStateDao(
        is_visible=src.is_visible, selected_child=src.selected_child
    )


def map_project_node_meta_state_from_dao(
    src: ProjectNodeMetaStateDao, mapper: Mapper
) -> ProjectNodeMetaState:
    return ProjectNodeMetaState(
        is_visible=src.is_visible, selected_child=src.selected_child
    )


def map_user_from_dao(src: UserDao, mapper: Mapper) -> User:
    return User(
        oauth_id=src.oauth_id,
        id=src.id,
        email=src.email,
        permissions=src.permissions,
        organization_id=src.organization_id,
    )


def map_user_to_dao(src: User, mapper: Mapper) -> UserDao:
    return UserDao(
        oauth_id=src.oauth_id,
        id=src.id,
        email=src.email,
        permissions=src.permissions,
        organization_id=src.organization_id,
    )


def map_organization_from_dao(src: OrganizationDao, mapper: Mapper) -> Organization:
    return Organization(
        id=src.id,
        name=src.name,
        email=src.email,
        limits=mapper.map(src.limits, OrganizationLimits),
    )


def map_organization_to_dao(src: Organization, mapper: Mapper) -> OrganizationDao:
    return OrganizationDao(
        id=src.id,
        name=src.name,
        email=src.email,
        limits=mapper.map(src.limits, OrganizationLimitsDao),
    )


def map_organization_limits_from_dao(
    src: OrganizationLimitsDao, mapper: Mapper
) -> OrganizationLimits:
    return OrganizationLimits(
        active_project_count=src.active_project_count,
        active_project_overall_collection_count=src.active_project_overall_collection_count,
        active_datasheet_count=src.active_datasheet_count,
        active_datasheet_custom_element_count=src.active_datasheet_custom_element_count,
    )


def map_organization_limits_to_dao(
    src: OrganizationLimits, mapper: Mapper
) -> OrganizationLimitsDao:
    return OrganizationLimitsDao(
        active_project_count=src.active_project_count,
        active_project_overall_collection_count=src.active_project_overall_collection_count,
        active_datasheet_count=src.active_datasheet_count,
        active_datasheet_custom_element_count=src.active_datasheet_custom_element_count,
    )


def map_ressource_from_dao(src: RessourceDao, mapper: Mapper) -> Ressource:
    return Ressource(
        id=src.id,
        kind=src.kind,
        organization_id=src.organization_id,
        permissions=src.permissions,
        name=src.name,
        creation_date_utc=src.creation_date_utc,
    )


def map_ressource_to_dao(src: Ressource, mapper: Mapper) -> RessourceDao:
    return RessourceDao(
        id=src.id,
        kind=src.kind,
        organization_id=src.organization_id,
        permissions=src.permissions,
        name=src.name,
        creation_date_utc=src.creation_date_utc,
        date_ordering=encode_date_with_uuid(src.creation_date_utc, src.id),
    )


def map_translation_from_dao(src: TranslationDao, mapper: Mapper) -> Translation:
    return Translation(
        ressource_id=src.ressource_id,
        locale=src.locale,
        scope=src.scope,
        name=src.name,
        value=src.value,
        creation_date_utc=src.creation_date_utc,
    )


def map_translation_to_dao(src: Translation, mapper: Mapper) -> TranslationDao:
    return TranslationDao(
        ressource_id=src.ressource_id,
        locale=src.locale,
        scope=src.scope,
        name=src.name,
        value=src.value,
        creation_date_utc=src.creation_date_utc,
        cursor=build_cursor(
            src.creation_date_utc,
            str(src.ressource_id),
            src.locale,
            src.name,
        ),
    )


def map_translation_id_to_dict(src: TranslationId, mapper: Mapper) -> dict:
    return dict(ressource_id=src.ressource_id, locale=src.locale, name=src.name)


def map_project_definition_node_filter_to_dict(
    src: ProjectDefinitionNodeFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "project_definition_id": ("project_definition_id", None),
            "name": ("name", None),
            "is_collection": ("is_collection", None),
            "instanciate_by_default": ("instanciate_by_default", None),
            "ordinal": ("ordinal", None),
            "path": ("path", join_uuid_path),
            "display_query_internal_id": ("display_query_internal_id", None),
        },
        type_of=DEFINITION_NODE_TYPE,
    )


def map_report_definition_filter(src: ReportDefinitionFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "project_definition_id": ("project_definition_id", None),
            "distributable": ("distributable", None),
        },
    )


def map_project_definition_node_pluck_filter_to_dict(
    src: ProjectDefinitionNodePluckFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "names": ("name", None),
        },
    )


def map_project_node_filter_to_dict(src: ProjectNodeFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "project_id": ("project_id", None),
            "type_id": ("type_id", None),
            "path": ("path", join_uuid_path),
            "label": ("label", None),
            "level": ("level", None),
            "display_query_internal_id": ("display_query_internal_id", None),
        },
    )


def map_project_node_meta_filter_to_dict(
    src: ProjectNodeMetaFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "project_id": ("project_id", None),
            "type_id": ("type_id", None),
            "display_query_internal_id": ("display_query_internal_id", None),
            "state": (
                "state",
                lambda state: map_project_node_meta_state_to_dao(state, mapper),
            ),
        },
    )


def map_formula_to_dao(src: Formula, mapper: Mapper) -> ProjectDefinitionFormulaDao:
    return ProjectDefinitionFormulaDao(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        path=join_uuid_path(src.path),
        level=FIELD_LEVEL,
        display_query_internal_id=src.id,
        creation_date_utc=src.creation_date_utc,
        config=FormulaConfigDao(
            attached_to_type_id=src.attached_to_type_id,
            expression=src.expression,
            dependency_graph=FormulaDependencyGraphDao(
                formulas=[
                    FormulaDependencyDao(
                        target_type_id=dependency.target_type_id, name=dependency.name
                    )
                    for dependency in src.dependency_graph.formulas
                ],
                nodes=[
                    FormulaDependencyDao(
                        target_type_id=dependency.target_type_id, name=dependency.name
                    )
                    for dependency in src.dependency_graph.nodes
                ],
            ),
        ),
    )


def map_formula_from_dao(src: ProjectDefinitionFormulaDao, mapper: Mapper) -> Formula:
    return Formula(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        path=split_uuid_path(src.path),
        expression=src.config.expression,
        creation_date_utc=src.creation_date_utc,
        attached_to_type_id=src.config.attached_to_type_id,
        dependency_graph=FormulaDependencyGraph(
            formulas=[
                FormulaDependency(
                    target_type_id=dependency.target_type_id, name=dependency.name
                )
                for dependency in src.config.dependency_graph.formulas
            ],
            nodes=[
                FormulaDependency(
                    target_type_id=dependency.target_type_id, name=dependency.name
                )
                for dependency in src.config.dependency_graph.nodes
            ],
        ),
    )


def map_staged_formula_to_dao(src: StagedFormula, mapper: Mapper) -> StagedFormulaDao:
    return StagedFormulaDao(
        id=src.id,
        project_definition_id=src.project_definition_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
        final_ast=src.final_ast,
        dependency_graph=FormulaDependencyGraphDao(
            formulas=[
                FormulaDependencyDao(
                    target_type_id=dependency.target_type_id, name=dependency.name
                )
                for dependency in src.dependency_graph.formulas
            ],
            nodes=[
                FormulaDependencyDao(
                    target_type_id=dependency.target_type_id, name=dependency.name
                )
                for dependency in src.dependency_graph.nodes
            ],
        ),
    )


def map_staged_formula_from_dao(src: StagedFormulaDao, mapper: Mapper) -> StagedFormula:
    return StagedFormula(
        id=src.id,
        project_definition_id=src.project_definition_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
        final_ast=src.final_ast,
        dependency_graph=FormulaDependencyGraph(
            formulas=[
                FormulaDependency(
                    target_type_id=dependency.target_type_id, name=dependency.name
                )
                for dependency in src.dependency_graph.formulas
            ],
            nodes=[
                FormulaDependency(
                    target_type_id=dependency.target_type_id, name=dependency.name
                )
                for dependency in src.dependency_graph.nodes
            ],
        ),
        path=formula.path,
        creation_date_utc=formula.creation_date_utc,
    )


def map_aggregate_collection_to_dao(
    src: AggregateCollection, mapper: Mapper
) -> AggregateCollectionDao:
    return AggregateCollectionDao(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        is_abstract=src.is_abstract,
        attributes_schema=[
            mapper.map(attribute_schema, AggregateAttributeSchemaDao)
            for attribute_schema in src.attributes_schema.values()
        ],
    )


def map_aggregate_collection_from_dao(
    src: AggregateCollectionDao, mapper: Mapper
) -> AggregateCollection:
    return AggregateCollection(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        is_abstract=src.is_abstract,
        attributes_schema={
            attribute_schema.name: mapper.map(
                attribute_schema, AggregateAttributeSchema
            )
            for attribute_schema in src.attributes_schema
        },
    )


def map_aggregate_attribute_schema_from_dao(
    src: AggregateAttributeSchemaDao, mapper: Mapper
) -> AggregateAttributeSchema:
    return AggregateAttributeSchema(
        name=src.name,
        details=mapper.map(src.details, field_details_to_domain_map.from_origin),
    )


def map_aggregate_attributeschema_to_dao(
    src: AggregateAttributeSchema, mapper: Mapper
) -> AggregateAttributeSchemaDao:
    return AggregateAttributeSchemaDao(
        name=src.name,
        details=mapper.map(src.details, field_details_to_domain_map.to_origin),
    )


def map_aggregate_to_dao(src: Aggregate, mapper: Mapper) -> AggregateDao:
    return AggregateDao(
        id=src.id,
        project_definition_id=src.project_definition_id,
        collection_id=src.collection_id,
        ordinal=src.ordinal,
        name=src.name,
        is_extendable=src.is_extendable,
        attributes=[
            mapper.map(attribute, AggregateAttributeDao)
            for attribute in src.attributes.values()
        ],
    )


def map_aggregate_from_dao(src: AggregateDao, mapper: Mapper) -> Aggregate:
    return Aggregate(
        id=src.id,
        project_definition_id=src.project_definition_id,
        collection_id=src.collection_id,
        ordinal=src.ordinal,
        name=src.name,
        is_extendable=src.is_extendable,
        attributes={
            attribute.name: mapper.map(attribute, AggregateAttribute)
            for attribute in src.attributes
        },
    )


def map_aggregate_attribute_from_dao(
    src: AggregateAttributeDao, mapper: Mapper
) -> AggregateAttribute:
    return AggregateAttribute(
        name=src.name,
        is_readonly=src.is_readonly,
        value=mapper.map(
            src.value, primitive_with_reference_union_dao_mappings.from_origin
        ),
    )


def map_aggregate_attribute_to_dao(
    src: AggregateAttribute, mapper: Mapper
) -> AggregateAttributeDao:
    return AggregateAttributeDao(
        name=src.name,
        is_readonly=src.is_readonly,
        value=mapper.map(
            src.value, primitive_with_reference_union_dao_mappings.to_origin
        ),
    )


def map_string_field_value_from_dao(src: StringFieldValueDao, mapper: Mapper) -> str:
    return src.text


def map_string_field_value_to_dao(src: str, mapper: Mapper) -> StringFieldValueDao:
    return StringFieldValueDao(text=src)


def map_bool_field_value_from_dao(src: BoolFieldValueDao, mapper: Mapper) -> bool:
    return src.enabled


def map_bool_field_value_to_dao(src: bool, mapper: Mapper) -> BoolFieldValueDao:
    return BoolFieldValueDao(enabled=src)


def map_int_field_value_from_dao(src: IntFieldValueDao, mapper: Mapper) -> int:
    return src.integer


def map_int_field_value_to_dao(src: int, mapper: Mapper) -> IntFieldValueDao:
    return IntFieldValueDao(integer=src)


def map_decimal_field_value_from_dao(
    src: DecimalFieldValueDao, mapper: Mapper
) -> Decimal:
    return src.numeric


def map_decimal_field_value_to_dao(
    src: Decimal, mapper: Mapper
) -> DecimalFieldValueDao:
    return DecimalFieldValueDao(numeric=src)


def map_reference_id_to_dao(src: UUID, mapper: Mapper) -> ReferenceIdDao:
    return ReferenceIdDao(uuid=src)


def map_reference_id_from_dao(src: ReferenceIdDao, mapper: Mapper) -> UUID:
    return src.uuid


def map_datasheet_to_dao(src: Datasheet, mapper: Mapper) -> DatasheetDao:
    return DatasheetDao(
        id=src.id,
        name=src.name,
        project_definition_id=src.project_definition_id,
        abstract_collection_id=src.abstract_collection_id,
        from_datasheet_id=src.from_datasheet_id,
        attributes_schema={
            name: mapper.map(attribute_schema, AggregateAttributeSchemaDao)
            for name, attribute_schema in src.attributes_schema.items()
        },
        instances_schema={
            str(id): mapper.map(instance_schema, InstanceSchemaDao)
            for id, instance_schema in src.instances_schema.items()
        },
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_from_dao(src: DatasheetDao, mapper: Mapper) -> Datasheet:
    return Datasheet(
        id=src.id,
        name=src.name,
        project_definition_id=src.project_definition_id,
        abstract_collection_id=src.abstract_collection_id,
        from_datasheet_id=src.from_datasheet_id,
        attributes_schema={
            name: mapper.map(attribute_schema, AggregateAttributeSchema)
            for name, attribute_schema in src.attributes_schema.items()
        },
        instances_schema={
            UUID(id): mapper.map(instance_schema, InstanceSchema)
            for id, instance_schema in src.instances_schema.items()
        },
        creation_date_utc=src.creation_date_utc,
    )


def map_instance_schema_from_dao(
    src: InstanceSchemaDao, mapper: Mapper
) -> InstanceSchema:
    return InstanceSchema(
        is_extendable=src.is_extendable,
        attributes_schema={
            name: mapper.map(attribute_schema, AggregateAttribute)
            for name, attribute_schema in src.attributes_schema.items()
        },
    )


def map_instance_schema_to_dao(
    src: InstanceSchema, mapper: Mapper
) -> InstanceSchemaDao:
    return InstanceSchemaDao(
        is_extendable=src.is_extendable,
        attributes_schema={
            name: mapper.map(attribute_schema, AggregateAttributeDao)
            for name, attribute_schema in src.attributes_schema.items()
        },
    )


def map_datasheet_element_to_dao(
    src: DatasheetElement, mapper: Mapper
) -> DatasheetElementDao:
    return DatasheetElementDao(
        id=src.id,
        datasheet_id=src.datasheet_id,
        aggregate_id=src.aggregate_id,
        ordinal=src.ordinal,
        attributes={
            attribute.name: mapper.map(attribute, AttributeDao)
            for attribute in src.attributes
        },
        original_datasheet_id=src.original_datasheet_id,
        original_owner_organization_id=src.original_owner_organization_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_from_dao(
    src: DatasheetElementDao, mapper: Mapper
) -> DatasheetElement:
    return DatasheetElement(
        id=src.id,
        datasheet_id=src.datasheet_id,
        aggregate_id=src.aggregate_id,
        ordinal=src.ordinal,
        attributes=[
            mapper.map(attribute, Attribute) for attribute in src.attributes.values()
        ],
        original_datasheet_id=src.original_datasheet_id,
        original_owner_organization_id=src.original_owner_organization_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_filter_to_dict(src: DatasheetFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "name": ("name", None),
            "project_definition_id": ("project_definition_id", None),
            "from_datasheet_id": ("from_datasheet_id", None),
            "creation_date_utc": ("creation_date_utc", None),
        },
    )


def map_translation_filter(src: TranslationFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "ressource_id": ("ressource_id", None),
            "locale": ("locale", None),
            "scope": ("scope", None),
            "name": ("name", None),
            "value": ("value", None),
            "creation_date_utc": ("creation_date_utc", None),
        },
    )


def map_ressource_filter(src: UserFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {"id": ("id", None)},
    )


def map_user_filter(src: UserFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {"id": ("id", None), "organization_id": ("organization_id", None)},
    )


def map_ressource_id_filter(src: RessourceId, mapper: Mapper) -> dict:
    return {"id": src.id, "organization_id": src.organization_id}


def map_formula_filter(src: FormulaFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "project_definition_id": ("project_definition_id", None),
            "attached_to_type_id": ("attached_to_type_id", None),
            "name": ("name", None),
            "expression": ("expression", None),
        },
        type_of=FORMULA_TYPE,
    )


def map_fomula_pluck_filter(src: FormulaPluckFilter, mapper: Mapper) -> Pluck:
    pluck_filter = map_dict_keys(
        src.args,
        {
            "ids": ("id", None),
            "names": ("name", None),
            "attached_to_type_ids": ("attached_to_type_id", None),
        },
    )

    if len(pluck_filter) != 1:
        raise Exception(
            f"Pluck filter must be applied on one key {pluck_filter.keys()}"
        )

    return Pluck(
        name=next(iter(pluck_filter.keys())),
        ids=next(iter(pluck_filter.values())),
    )


def map_fomula_pluck_subresource_filter(
    src: FormulaPluckFilter, mapper: Mapper
) -> PluckSubRessource:
    pluck_filter = map_dict_keys(
        src.args,
        {
            "ids": ("id", None),
            "names": ("name", None),
            "attached_to_type_ids": ("attached_to_type_id", None),
        },
    )

    if len(pluck_filter) != 1:
        raise Exception(
            f"Pluck filter must be applied on one key {pluck_filter.keys()}"
        )

    return PluckSubRessource(
        base=map_formula_filter(src, mapper),
        name=next(iter(pluck_filter.keys())),
        ids=next(iter(pluck_filter.values())),
    )


def map_project_node_values_to_dict(src: ProjectNodeValues, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "project_id": ("project_id", None),
            "type_id": ("type_id", None),
            "path": ("path", join_uuid_path),
            "value": (
                "value",
                lambda x: mapper.map(
                    x, primitive_with_none_union_dao_mappings.to_origin
                ),
            ),
            "label": ("label", None),
            "level": ("level", None),
            "display_query_internal_id": ("display_query_internal_id", None),
        },
    )


def map_node_pluck_filter(src: NodePluckFilter, mapper: Mapper) -> PluckSubRessource:
    pluck_filter = map_dict_keys(
        src.args,
        {"ids": ("id", None), "type_ids": ("type_id", None)},
    )

    if len(pluck_filter) != 1:
        raise Exception(
            f"Pluck filter must be applied on one key {pluck_filter.keys()}"
        )

    return Pluck(
        name=next(iter(pluck_filter.keys())),
        ids=next(iter(pluck_filter.values())),
    )


def map_node_pluck_subressource_filter(
    src: NodePluckFilter, mapper: Mapper
) -> PluckSubRessource:
    pluck_filter = map_dict_keys(
        src.args,
        {"ids": ("id", None), "type_ids": ("type_id", None)},
    )

    if len(pluck_filter) != 1:
        raise Exception(
            f"Pluck filter must be applied on one key {pluck_filter.keys()}"
        )

    return PluckSubRessource(
        base=map_project_node_values_to_dict(src, mapper),
        name=next(iter(pluck_filter.keys())),
        ids=next(iter(pluck_filter.values())),
    )


def map_measure_unit_from_dao(src: MeasureUnitDao, mapper: Mapper) -> MeasureUnit:
    return MeasureUnit(id=src.id)


def map_measure_unit_to_dao(src: MeasureUnit, mapper: Mapper) -> MeasureUnitDao:
    return MeasureUnitDao(id=src.id)


def map_report_definition_from_dao(
    src: ReportDefinitionDao, mapper: Mapper
) -> ReportDefinition:
    return ReportDefinition(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        structure=mapper.map(src.structure, ReportStructure),
        distributable=src.distributable,
    )


def map_report_definition_to_dao(
    src: ReportDefinition, mapper: Mapper
) -> ReportDefinitionDao:
    return ReportDefinitionDao(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        structure=mapper.map(src.structure, ReportStructureDao),
        distributable=src.distributable,
    )


def map_report_structure_from_dao(
    src: ReportStructureDao, mapper: Mapper
) -> ReportStructure:
    return ReportStructure(
        datasheet_selection_alias=src.datasheet_selection_alias,
        formula_attribute=mapper.map(src.formula_attribute, AttributeBucket),
        datasheet_attribute=mapper.map(src.datasheet_attribute, AttributeBucket),
        stage_summary=mapper.map(src.stage_summary, ReportComputation),
        report_summary=mapper.map_many(src.report_summary, ReportComputation),
        joins_cache=mapper.map_many(src.joins_cache, ReportJoin),
        columns=mapper.map_many(src.columns, ReportComputation),
        group_by=mapper.map_many(src.group_by, AttributeBucket),
        order_by=mapper.map_many(src.order_by, AttributeBucket),
    )


def map_report_structure_to_dao(
    src: ReportStructure, mapper: Mapper
) -> ReportStructureDao:
    return ReportStructureDao(
        datasheet_selection_alias=src.datasheet_selection_alias,
        formula_attribute=mapper.map(src.formula_attribute, AttributeBucketDao),
        datasheet_attribute=mapper.map(src.datasheet_attribute, AttributeBucketDao),
        stage_summary=mapper.map(src.stage_summary, ReportComputationyDao),
        report_summary=mapper.map_many(src.report_summary, ReportComputationDao),
        joins_cache=mapper.map_many(src.joins_cache, ReportJoinDao),
        columns=mapper.map_many(src.columns, ReportComputationDao),
        group_by=mapper.map_many(src.group_by, AttributeBucketDao),
        order_by=mapper.map_many(src.order_by, AttributeBucketDao),
    )


def map_report_computation_to_dao(
    src: ReportComputation, mapper: Mapper
) -> ReportComputationDao:
    return ReportComputationDao(
        name=src.name,
        is_visible=src.is_visible,
        expression=src.expression,
        unit=mapper.map(src.unit, AttributeBucketDao)
        if isinstance(src.unit, AttributeBucket)
        else src.unit,
    )


def map_report_computation_from_dao(
    src: ReportComputationDao, mapper: Mapper
) -> ReportComputation:
    return ReportComputation(
        name=src.name,
        is_visible=src.is_visible,
        expression=src.expression,
        unit=mapper.map(src.unit, AttributeBucket)
        if isinstance(src.unit, AttributeBucketDao)
        else src.unit,
    )


def map_attribute_bucket_from_dao(
    src: AttributeBucketDao, mapper: Mapper
) -> AttributeBucket:
    return AttributeBucket(
        bucket_name=src.bucket_name, attribute_name=src.attribute_name
    )


def map_attribute_bucket_to_dao(
    src: AttributeBucket, mapper: Mapper
) -> AttributeBucketDao:
    return AttributeBucketDao(
        bucket_name=src.bucket_name, attribute_name=src.attribute_name
    )


def map_report_join_from_dao(src: ReportJoinDao, mapper: Mapper) -> ReportJoin:
    return ReportJoin(
        from_object_name=src.from_object_name,
        from_property_name=src.from_property_name,
        join_on_collection=src.join_on_collection,
        join_on_attribute=src.join_on_attribute,
        alias_name=src.alias_name,
        warn_about_idle_items=src.warn_about_idle_items,
        same_cardinality=src.same_cardinality,
        allow_dicard_element=src.allow_dicard_element,
    )


def map_report_join_to_dao(src: ReportJoin, mapper: Mapper) -> ReportJoinDao:
    return ReportJoinDao(
        from_object_name=src.from_object_name,
        from_property_name=src.from_property_name,
        join_on_collection=src.join_on_collection,
        join_on_attribute=src.join_on_attribute,
        alias_name=src.alias_name,
        warn_about_idle_items=src.warn_about_idle_items,
        same_cardinality=src.same_cardinality,
        allow_dicard_element=src.allow_dicard_element,
    )


def map_aggregate_collection_filter(
    src: AggregateCollectionFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "project_definition_id": ("project_definition_id", None),
            "name": ("name", None),
        },
    )


def map_translation_pluck_filter_to_dict(
    src: TranslationPluckFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "scopes": ("scope", None),
        },
    )


def map_report_row_filter(src: ReportRowFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "project_id": ("project_id", None),
            "report_def_id": ("report_def_id", None),
            "datasheet_id": ("datasheet_id", None),
            "element_id": ("element_id", None),
            "element_id": ("element_id", None),
        },
    )


def map_datasheet_element_filter_to_dict(
    src: DatasheetElementFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "datasheet_id": ("datasheet_id", None),
            "aggregate_id": ("aggregate_id", None),
            "ordinal": ("ordinal", None),
            "original_datasheet_id": ("original_datasheet_id", None),
            "original_owner_organization_id": ("original_owner_organization_id", None),
            "creation_date_utc": ("creation_date_utc", None),
        },
    )


def map_datasheet_element_pluck_filter(
    src: DatasheetElementPluckFilter, mapper: Mapper
) -> Pluck:
    pluck_filter = map_dict_keys(
        src.args,
        {
            "aggregate_ids": ("aggregate_id", None),
            "ids": ("id", None),
        },
    )

    if len(pluck_filter) != 1:
        raise Exception(
            f"Pluck filter must be applied on one key {pluck_filter.keys()}"
        )

    return Pluck(
        name=next(iter(pluck_filter.keys())),
        ids=next(iter(pluck_filter.values())),
    )


def map_datasheet_element_pluck_subressource_filter(
    src: DatasheetElementPluckFilter, mapper: Mapper
) -> PluckSubRessource:
    pluck_filter = map_dict_keys(
        src.args,
        {
            "aggregate_ids": ("aggregate_id", None),
            "ids": ("id", None),
        },
    )

    if len(pluck_filter) != 1:
        raise Exception(
            f"Pluck filter must be applied on one key {pluck_filter.keys()}"
        )

    return PluckSubRessource(
        base=map_datasheet_element_filter_to_dict(src, mapper),
        name=next(iter(pluck_filter.keys())),
        ids=next(iter(pluck_filter.values())),
    )


def map_computed_value_to_dao(src: ComputedValue, mapper: Mapper) -> ComputedValueDao:
    return ComputedValueDao(
        label=src.label,
        value=mapper.map(src.value, primitive_union_dao_mappings.to_origin),
        unit=src.unit,
        is_visible=src.is_visible,
    )


def map_computed_value_from_dao(src: ComputedValueDao, mapper: Mapper) -> ComputedValue:
    return ComputedValue(
        label=src.label,
        value=mapper.map(src.value, primitive_union_dao_mappings.from_origin),
        unit=src.unit,
        is_visible=src.is_visible,
    )


def map_report_to_dao(src: Report, mapper: Mapper) -> ReportDao:
    return ReportDao(
        name=src.name,
        datasheet_id=src.datasheet_id,
        creation_date_utc=src.creation_date_utc,
        summaries=mapper.map_many(src.summaries, ComputedValueDao),
        stages=mapper.map_many(src.stages, ReportStageDao),
    )


def map_report_from_dao(src: ReportDao, mapper: Mapper) -> Report:
    return Report(
        name=src.name,
        datasheet_id=src.datasheet_id,
        creation_date_utc=src.creation_date_utc,
        summaries=mapper.map_many(src.summaries, ComputedValue),
        stages=mapper.map_many(src.stages, ReportStage),
    )


def map_report_group_to_dao(src: ReportStage, mapper: Mapper) -> ReportStageDao:
    return ReportStageDao(
        summary=mapper.map(src.summary, ComputedValueDao),
        columns=mapper.map_many(src.columns, StageColumnDao),
        rows=mapper.map_many(src.rows, ReportRowDao),
    )


def map_stage_column_to_dao(src: StageColumn, mapper: Mapper) -> StageColumnDao:
    return StageColumnDao(
        label=src.label,
        unit=src.unit,
        is_visible=src.is_visible,
    )


def map_stage_column_from_dao(src: StageColumnDao, mapper: Mapper) -> StageColumn:
    return StageColumn(
        label=src.label,
        unit=src.unit,
        is_visible=src.is_visible,
    )


def map_report_group_from_dao(src: ReportStageDao, mapper: Mapper) -> ReportStage:
    return ReportStage(
        summary=mapper.map(src.summary, ComputedValue),
        rows=mapper.map_many(src.rows, ReportRow),
    )


def map_report_row_to_dao(src: ReportRow, mapper: Mapper) -> ReportRowDao:
    return ReportRowDao(
        node_id=src.node_id,
        formula_id=src.formula_id,
        aggregate_id=src.aggregate_id,
        element_id=src.element_id,
        columns=mapper.map_many(src.columns, ComputedValueDao),
        row=map_report_rows_dict_to_dao(src.row, mapper),
    )


def map_report_row_from_dao(src: ReportRowDao, mapper: Mapper) -> ReportRow:
    return ReportRow(
        node_id=src.node_id,
        formula_id=src.formula_id,
        aggregate_id=src.aggregate_id,
        element_id=src.element_id,
        columns=mapper.map_many(src.columns, ComputedValue),
        row=map_report_rows_dict_from_dao(src.row, mapper),
    )


def map_report_rows_dict_to_dao(src: ReportRowDict, mapper: Mapper) -> ReportRowDictDao:
    return {
        name: {
            attr_name: mapper.map_many(attribute, ReferenceIdDao)
            if isinstance(attribute, list)
            else mapper.map(
                attribute, primitive_with_reference_union_dao_mappings.to_origin
            )
            for attr_name, attribute in bucket.items()
        }
        for name, bucket in src.items()
    }


def map_report_rows_dict_from_dao(
    src: ReportRowDictDao, mapper: Mapper
) -> ReportRowDict:
    return {
        name: {
            attr_name: mapper.map_many(attribute, UUID)
            if isinstance(attribute, list)
            else mapper.map(
                attribute, primitive_with_reference_union_dao_mappings.from_origin
            )
            for attr_name, attribute in bucket.items()
        }
        for name, bucket in src.items()
    }


def map_ressource_filter_to_dict(src: RessourceFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "organization_id": ("organization_id", None),
            "organization_id": ("organization_id", None),
        },
    )


def map_distributable_id_to_dict(src: DistributableItemFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "project_id": ("project_id", None),
            "report_definition_id": ("report_definition_id", None),
        },
    )


def map_distributable_item_from_dao(
    src: DistributableItemDao, mapper: Mapper
) -> DistributableItem:
    return DistributableItem(
        project_id=src.project_id,
        report_definition_id=src.report_definition_id,
        node_id=src.node_id,
        formula_id=src.formula_id,
        supplied_item=SuppliedItem(
            datasheet_id=src.supplied_item.datasheet_id,
            aggregate_id=src.supplied_item.aggregate_id,
            element_id=src.supplied_item.element_id,
            organization_id=src.supplied_item.organization_id,
        ),
        distribution_ids=src.distribution_ids,
        summary=mapper.map(src.summary, ComputedValue),
        columns=mapper.map_many(src.columns, ComputedValue),
        obsolete=src.obsolete,
        creation_date_utc=src.creation_date_utc,
    )


def map_distributable_item_to_dao(
    src: DistributableItem, mapper: Mapper
) -> DistributableItemDao:
    return DistributableItemDao(
        project_id=src.project_id,
        report_definition_id=src.report_definition_id,
        node_id=src.node_id,
        formula_id=src.formula_id,
        supplied_item=SuppliedItemDao(
            datasheet_id=src.supplied_item.datasheet_id,
            aggregate_id=src.supplied_item.aggregate_id,
            element_id=src.supplied_item.element_id,
            organization_id=src.supplied_item.organization_id,
        ),
        distribution_ids=src.distribution_ids,
        summary=mapper.map(src.summary, ComputedValueDao),
        columns=mapper.map_many(src.columns, ComputedValueDao),
        obsolete=src.obsolete,
        creation_date_utc=src.creation_date_utc,
    )


def map_aggregate_filter_to_dict(src: AggregateFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "project_definition_id": ("project_definition_id", None),
            "collection_id": ("collection_id", None),
            "ordinal": ("ordinal", None),
            "name": ("name", None),
        },
    )


def map_attribute_from_dao(src: AttributeDao, mapper: Mapper) -> Attribute:
    return Attribute(
        name=src.name,
        value=mapper.map(
            src.value, primitive_with_reference_union_dao_mappings.from_origin
        ),
    )


def map_attribute_to_dao(src: Attribute, mapper: Mapper) -> AttributeDao:
    return AttributeDao(
        name=src.name,
        value=mapper.map(
            src.value, primitive_with_reference_union_dao_mappings.to_origin
        ),
    )

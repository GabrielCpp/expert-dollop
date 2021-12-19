from typing import List
from uuid import UUID
from expert_dollup.shared.starlette_injection import Clock
from expert_dollup.shared.automapping import (
    Mapper,
    map_dict_keys,
    RevervibleUnionMapping,
)
from expert_dollup.core.utils.path_transform import (
    split_uuid_path,
    join_uuid_path,
    list_uuid_to_str,
    list_str_to_uuid,
)

from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.core.domains import *


def get_display_query_id(global_id: UUID, path: List[UUID]) -> str:
    display_query_internal_id = global_id
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
        default_datasheet_id=src.default_datasheet_id,
        datasheet_def_id=src.datasheet_def_id,
    )


def map_project_definition_to_dao(
    src: ProjectDefinition, mapper: Mapper
) -> ProjectDefinitionDao:
    return ProjectDefinitionDao(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        datasheet_def_id=src.datasheet_def_id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_project_definition_node_from_dao(
    src: ProjectDefinitionNodeDao, mapper: Mapper
) -> ProjectDefinitionNode:
    return ProjectDefinitionNode(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        config=mapper.map(src.config, NodeConfig, NodeConfigDao),
        default_value=src.default_value,
        path=split_uuid_path(src.path),
        creation_date_utc=src.creation_date_utc,
    )


def map_node_config_from_dao(src: NodeConfigDao, mapper: Mapper) -> NodeConfig:
    return NodeConfig(
        translations=TranslationConfig(
            help_text_name=src.translations.help_text_name, label=src.translations.label
        ),
        triggers=[
            Trigger(
                action=TriggerAction(trigger.action),
                target_type_id=trigger.target_type_id,
                params=trigger.params,
            )
            for trigger in src.triggers
        ],
        meta=NodeMetaConfig(is_visible=src.meta.is_visible),
        field_details=mapper.map(
            src.field_details, FieldDetailsUnion, FieldDetailsUnionDao
        ),
        value_validator=src.value_validator,
    )


def map_node_config_to_dao(src: NodeConfig, mapper: Mapper) -> NodeConfigDao:
    return NodeConfigDao(
        translations=TranslationConfigDao(
            help_text_name=src.translations.help_text_name, label=src.translations.label
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
            src.field_details, FieldDetailsUnionDao, FieldDetailsUnion
        ),
        value_validator=src.value_validator,
    )


def map_field_details_union_from_dao(
    src: FieldDetailsUnionDao, mapper: Mapper
) -> FieldDetailsUnion:
    if src is None:
        return None

    assert isinstance(
        src,
        (
            IntFieldConfigDao,
            DecimalFieldConfigDao,
            StringFieldConfigDao,
            BoolFieldConfigDao,
            StaticChoiceFieldConfigDao,
            CollapsibleContainerFieldConfigDao,
            StaticNumberFieldConfigDao,
        ),
    )

    if isinstance(src, IntFieldConfigDao):
        return IntFieldConfig(unit=src.unit)

    if isinstance(src, DecimalFieldConfigDao):
        return DecimalFieldConfig(unit=src.unit, precision=src.precision)

    if isinstance(src, StringFieldConfigDao):
        return StringFieldConfig(
            transforms=src.transforms,
        )

    if isinstance(src, BoolFieldConfigDao):
        return BoolFieldConfig(is_checkbox=src.is_checkbox)

    if isinstance(src, StaticChoiceFieldConfigDao):
        return StaticChoiceFieldConfig(
            options=[
                StaticChoiceOption(
                    id=option.id,
                    label=option.label,
                    help_text=option.help_text,
                )
                for option in src.options
            ]
        )

    if isinstance(src, CollapsibleContainerFieldConfigDao):
        return CollapsibleContainerFieldConfig(is_collapsible=src.is_collapsible)

    if isinstance(src, StaticNumberFieldConfigDao):
        return StaticNumberFieldConfig(
            pass_to_translation=src.pass_to_translation,
            precision=src.precision,
            unit=src.unit,
        )


def map_field_details_union_to_dao(
    src: FieldDetailsUnion, mapper: Mapper
) -> FieldDetailsUnionDao:
    if src is None:
        return None

    assert isinstance(
        src,
        (
            IntFieldConfig,
            DecimalFieldConfig,
            StringFieldConfig,
            BoolFieldConfig,
            StaticChoiceFieldConfig,
            CollapsibleContainerFieldConfig,
            StaticNumberFieldConfig,
        ),
    )

    if isinstance(src, IntFieldConfig):
        return IntFieldConfigDao(unit=src.unit)

    if isinstance(src, DecimalFieldConfig):
        return DecimalFieldConfigDao(unit=src.unit, precision=src.precision)

    if isinstance(src, StringFieldConfig):
        return StringFieldConfigDao(
            transforms=src.transforms,
        )

    if isinstance(src, BoolFieldConfig):
        return BoolFieldConfigDao(is_checkbox=src.is_checkbox)

    if isinstance(src, StaticChoiceFieldConfig):
        return StaticChoiceFieldConfigDao(
            options=[
                StaticChoiceOptionDao(
                    id=option.id,
                    label=option.label,
                    help_text=option.help_text,
                )
                for option in src.options
            ]
        )

    if isinstance(src, CollapsibleContainerFieldConfig):
        return CollapsibleContainerFieldConfigDao(is_collapsible=src.is_collapsible)

    if isinstance(src, StaticNumberFieldConfig):
        return StaticNumberFieldConfigDao(
            pass_to_translation=src.pass_to_translation,
            precision=src.precision,
            unit=src.unit,
        )


def map_project_definition_node_to_dao(
    src: ProjectDefinitionNode, mapper: Mapper
) -> ProjectDefinitionNodeDao:
    display_query_internal_id = get_display_query_id(src.project_def_id, src.path)

    return ProjectDefinitionNodeDao(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        config=mapper.map(src.config, NodeConfigDao),
        path=join_uuid_path(src.path),
        display_query_internal_id=display_query_internal_id,
        level=len(src.path),
        creation_date_utc=mapper.get(Clock).utcnow(),
        default_value=src.default_value,
    )


def map_project_from_dao(src: ProjectDao, mapper: Mapper) -> ProjectDetails:
    return ProjectDetails(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_project_to_dao(src: ProjectDetails, mapper: Mapper) -> ProjectDao:
    return ProjectDao(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_project_node_to_dao(src: ProjectNode, mapper: Mapper) -> ProjectNodeDao:
    display_query_internal_id = get_display_query_id(src.project_id, src.path)

    return ProjectNodeDao(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        type_name=src.type_name,
        path=join_uuid_path(src.path),
        value=src.value,
        label=src.label,
        type_path=join_uuid_path(src.type_path),
        level=len(src.path),
        display_query_internal_id=display_query_internal_id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_project_node_from_dao(src: ProjectNodeDao, mapper: Mapper) -> ProjectNode:
    return ProjectNode(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        type_name=src.type_name,
        path=split_uuid_path(src.path),
        type_path=split_uuid_path(src.type_path),
        value=src.value,
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


def map_ressource_from_dao(src: RessourceDao, mapper: Mapper) -> Ressource:
    return Ressource(
        id=src.id,
        name=src.name,
        owner_id=src.owner_id,
    )


def map_ressource_to_dao(src: Ressource, mapper: Mapper) -> RessourceDao:
    return RessourceDao(
        id=src.id,
        name=src.name,
        owner_id=src.owner_id,
    )


def map_translation_from_dao(src: TranslationDao, mapper: Mapper) -> Translation:
    return Translation(
        id=src.id,
        ressource_id=src.ressource_id,
        locale=src.locale,
        scope=src.scope,
        name=src.name,
        value=src.value,
        creation_date_utc=src.creation_date_utc,
    )


def map_translation_to_dao(src: Translation, mapper: Mapper) -> TranslationDao:
    return TranslationDao(
        id=src.id,
        ressource_id=src.ressource_id,
        locale=src.locale,
        scope=src.scope,
        name=src.name,
        value=src.value,
        creation_date_utc=src.creation_date_utc,
    )


def map_translation_id_to_dict(src: TranslationId, mapper: Mapper) -> dict:
    return dict(
        ressource_id=src.ressource_id, scope=src.scope, locale=src.locale, name=src.name
    )


def map_project_definition_to_dao(
    src: ProjectDefinition, mapper: Mapper
) -> ProjectDefinitionDao:
    return ProjectDefinitionDao(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        datasheet_def_id=src.datasheet_def_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_project_definition_from_dao(
    src: ProjectDefinitionDao, mapper: Mapper
) -> ProjectDefinition:
    return ProjectDefinition(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        datasheet_def_id=src.datasheet_def_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_project_definition_node_filter_to_dict(
    src: ProjectDefinitionNodeFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "project_def_id": ("project_def_id", None),
            "name": ("name", None),
            "is_collection": ("is_collection", None),
            "instanciate_by_default": ("instanciate_by_default", None),
            "order_index": ("order_index", None),
            "default_value": ("default_value", None),
            "path": ("path", join_uuid_path),
            "display_query_internal_id": ("display_query_internal_id", None),
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
            "value": ("value", None),
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
        project_def_id=src.project_def_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
        dependency_graph=FormulaDependencyGraphDao(
            formulas=[
                FormulaDependencyDao(target_type_id=dependency.target_type_id)
                for dependency in src.dependency_graph.formulas
            ],
            nodes=[
                FormulaDependencyDao(target_type_id=dependency.target_type_id)
                for dependency in src.dependency_graph.nodes
            ],
        ),
    )


def map_formula_from_dao(src: ProjectDefinitionFormulaDao, mapper: Mapper) -> Formula:
    return Formula(
        id=src.id,
        project_def_id=src.project_def_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
        dependency_graph=FormulaDependencyGraph(
            formulas=[
                FormulaDependency(target_type_id=dependency.target_type_id)
                for dependency in src.dependency_graph.formulas
            ],
            nodes=[
                FormulaDependency(target_type_id=dependency.target_type_id)
                for dependency in src.dependency_graph.nodes
            ],
        ),
    )


def map_formula_cache_result_to_dao(
    src: FormulaCachedResult, mapper: Mapper
) -> ProjectFormulaCacheDao:
    return ProjectFormulaCacheDao(
        project_id=src.project_id,
        formula_id=src.formula_id,
        node_id=src.node_id,
        calculation_details=src.calculation_details,
        result=src.result,
        last_modified_date_utc=mapper.get(Clock).utcnow(),
    )


def map_formula_cache_result_from_dao(
    src: ProjectFormulaCacheDao, mapper: Mapper
) -> FormulaCachedResult:
    return FormulaCachedResult(
        project_id=src.project_id,
        formula_id=src.formula_id,
        node_id=src.node_id,
        calculation_details=src.calculation_details,
        result=src.result,
    )


def map_datasheet_definition_to_dao(
    src: DatasheetDefinition, mapper: Mapper
) -> DatasheetDefinitionDao:
    return DatasheetDefinitionDao(
        id=src.id,
        name=src.name,
        properties={
            key: mapper.map(element, ElementPropertySchemaDao)
            for key, element in src.properties.items()
        },
    )


def map_datasheet_definition_from_dao(
    src: DatasheetDefinitionDao, mapper: Mapper
) -> DatasheetDefinition:
    return DatasheetDefinition(
        id=src.id,
        name=src.name,
        properties={
            key: mapper.map(element, ElementPropertySchema, ElementPropertySchemaDao)
            for key, element in src.properties.items()
        },
    )


def map_element_property_schema_to_dao(
    src: ElementPropertySchema, mapper: Mapper
) -> ElementPropertySchemaDao:
    return ElementPropertySchemaDao(value_validator=src.value_validator)


def map_element_property_schema_from_dao(
    src: ElementPropertySchemaDao, mapper: Mapper
) -> ElementPropertySchema:
    return ElementPropertySchema(value_validator=src.value_validator)


def map_datasheet_definition_element_to_dao(
    src: DatasheetDefinitionElement, mapper: Mapper
) -> DatasheetDefinitionElementDao:
    return DatasheetDefinitionElementDao(
        id=src.id,
        unit_id=src.unit_id,
        is_collection=src.is_collection,
        name=src.name,
        datasheet_def_id=src.datasheet_def_id,
        order_index=src.order_index,
        default_properties={
            name: mapper.map(property_details, DatasheetDefinitionElementPropertyDao)
            for (name, property_details) in src.default_properties.items()
        },
        tags=list_uuid_to_str(src.tags),
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_definition_element_from_dao(
    src: DatasheetDefinitionElementDao, mapper: Mapper
) -> DatasheetDefinitionElement:
    return DatasheetDefinitionElement(
        id=src.id,
        unit_id=src.unit_id,
        is_collection=src.is_collection,
        name=src.name,
        datasheet_def_id=src.datasheet_def_id,
        order_index=src.order_index,
        default_properties={
            name: mapper.map(
                item_property,
                DatasheetDefinitionElementProperty,
                DatasheetDefinitionElementPropertyDao,
            )
            for name, item_property in src.default_properties.items()
        },
        tags=list_str_to_uuid(src.tags),
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_definition_element_property_to_dao(
    src: DatasheetDefinitionElementProperty, mapper: Mapper
) -> DatasheetDefinitionElementPropertyDao:
    return DatasheetDefinitionElementPropertyDao(
        is_readonly=src.is_readonly,
        value=src.value,
    )


def map_datasheet_definition_element_property_from_dao(
    src: DatasheetDefinitionElementPropertyDao, mapper: Mapper
) -> DatasheetDefinitionElementProperty:
    return DatasheetDefinitionElementProperty(
        is_readonly=src.is_readonly,
        value=src.value,
    )


def map_datasheet_definition_element_filter(
    src: DatasheetDefinitionElementFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "unit_id": ("unit_id", None),
            "is_collection": ("is_collection", None),
            "datasheet_def_id": ("datasheet_def_id", None),
            "order_index": ("order_index", None),
            "tags": ("tags", None),
            "creation_date_utc": ("creation_date_utc", None),
        },
    )


label_attribute_schema_dao_mappings = RevervibleUnionMapping(
    LabelAttributeSchemaDaoUnion, LabelAttributeSchemaUnion
)


def map_datasheet_definition_label_collection_from_dao(
    src: LabelCollectionDao, mapper: Mapper
) -> LabelCollection:
    return LabelCollection(
        id=src.id,
        datasheet_definition_id=src.datasheet_definition_id,
        name=src.name,
        attributes_schema=mapper.map_dict_values(
            src.attributes_schema, label_attribute_schema_dao_mappings.from_origin
        ),
    )


def map_datasheet_definition_label_collection_to_dao(
    src: LabelCollection, mapper: Mapper
) -> LabelCollectionDao:
    return LabelCollectionDao(
        id=src.id,
        datasheet_definition_id=src.datasheet_definition_id,
        name=src.name,
        attributes_schema=mapper.map_dict_values(
            src.attributes_schema, label_attribute_schema_dao_mappings.to_origin
        ),
    )


label_attribute_dao_mappings = RevervibleUnionMapping(
    LabelAttributeDaoUnion,
    LabelAttributeUnion,
    {
        StrictBool: bool,
        StrictInt: int,
        StrictStr: str,
        StrictFloat: float,
        ReferenceIdDao: UUID,
    },
)


def map_datasheet_definition_label_to_dao(src: Label, mapper: Mapper) -> LabelDao:
    return LabelDao(
        id=src.id,
        label_collection_id=src.label_collection_id,
        order_index=src.order_index,
        attributes=mapper.map_dict_values(
            src.attributes, label_attribute_dao_mappings.to_origin
        ),
    )


def map_datasheet_definition_label_from_dao(src: LabelDao, mapper: Mapper) -> Label:
    return Label(
        id=src.id,
        label_collection_id=src.label_collection_id,
        order_index=src.order_index,
        attributes=mapper.map_dict_values(
            src.attributes, label_attribute_dao_mappings.from_origin
        ),
    )


def map_datasheet_to_dao(src: Datasheet, mapper: Mapper) -> DatasheetDao:
    return DatasheetDao(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        datasheet_def_id=src.datasheet_def_id,
        from_datasheet_id=src.from_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_from_dao(src: DatasheetDao, mapper: Mapper) -> Datasheet:
    return Datasheet(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        datasheet_def_id=src.datasheet_def_id,
        from_datasheet_id=src.from_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_to_dao(
    src: DatasheetElement, mapper: Mapper
) -> DatasheetElementDao:
    return DatasheetElementDao(
        datasheet_id=src.datasheet_id,
        element_def_id=src.element_def_id,
        child_element_reference=src.child_element_reference,
        properties=src.properties,
        original_datasheet_id=src.original_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_from_dao(
    src: DatasheetElementDao, mapper: Mapper
) -> DatasheetElement:
    return DatasheetElement(
        datasheet_id=src.datasheet_id,
        element_def_id=src.element_def_id,
        child_element_reference=src.child_element_reference,
        properties=src.properties,
        original_datasheet_id=src.original_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_filter_to_dict(
    src: DatasheetElementFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "datasheet_id": ("datasheet_id", None),
            "element_def_id": ("element_def_id", None),
            "child_element_reference": ("child_element_reference", None),
            "properties": ("properties", None),
            "creation_date_utc": ("creation_date_utc", None),
        },
    )


def map_datasheet_element_id_to_dict(src: DatasheetElementId, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "datasheet_id": ("datasheet_id", None),
            "element_def_id": ("element_def_id", None),
            "child_element_reference": ("child_element_reference", None),
        },
    )


def map_datasheet_filter_to_dict(src: DatasheetFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "name": ("name", None),
            "is_staged": ("is_staged", None),
            "datasheet_def_id": ("datasheet_def_id", None),
            "from_datasheet_id": ("from_datasheet_id", None),
            "creation_date_utc": ("creation_date_utc", None),
        },
    )


def map_translation_ressource_locale_query_to_dict(
    src: TranslationRessourceLocaleQuery, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "ressource_id": ("ressource_id", None),
            "locale": ("locale", None),
        },
    )


def map_translation_filter(src: TranslationFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "ressource_id": ("ressource_id", None),
            "locale": ("locale", None),
            "scope": ("scope", None),
            "name": ("name", None),
            "value": ("value", None),
            "creation_date_utc": ("creation_date_utc", None),
        },
    )


def map_formula_filter(src: FormulaFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "project_def_id": ("project_def_id", None),
            "attached_to_type_id": ("attached_to_type_id", None),
            "name": ("name", None),
            "expression": ("expression", None),
        },
    )


def map_fomula_pluck_filter(src: FormulaPluckFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {
            "ids": ("id", None),
            "names": ("name", None),
            "attached_to_type_ids": ("attached_to_type_id", None),
        },
    )


def map_node_pluck_filter(src: NodePluckFilter, mapper: Mapper) -> dict:
    return map_dict_keys(
        src.args,
        {"ids": ("id", None)},
    )


def map_formula_cached_result_filter(
    src: FormulaCachedResultFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "project_id": ("project_id", None),
        },
    )


def map_report_definition_to_dao(
    src: ReportDefinition, mapper: Mapper
) -> ReportDefinitionDao:
    return ReportDefinitionDao(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        structure=ReportStructureDao(
            initial_selection=ReportJoinDao(
                to_object_name=src.structure.initial_selection.to_object_name,
                from_object_name=src.structure.initial_selection.from_object_name,
                join_on_property_name=src.structure.initial_selection.join_on_property_name,
            ),
            joins=[
                ReportJoinDao(
                    to_object_name=j.to_object_name,
                    from_object_name=j.from_object_name,
                    join_on_property_name=j.join_on_property_name,
                )
                for j in src.structure.joins
            ],
        ),
    )

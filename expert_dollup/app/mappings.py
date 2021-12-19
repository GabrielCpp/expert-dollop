from dataclasses import dataclass
from uuid import UUID, uuid4
from expert_dollup.shared.starlette_injection import Clock
from expert_dollup.shared.automapping import Mapper, RevervibleUnionMapping
from expert_dollup.shared.database_services import Page
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *


def map_project_definition_from_dto(
    src: ProjectDefinitionDto, mapper: Mapper
) -> ProjectDefinition:
    return ProjectDefinition(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        datasheet_def_id=src.datasheet_def_id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_project_definition_to_dto(
    src: ProjectDefinition, mapper: Mapper
) -> ProjectDefinitionDto:
    return ProjectDefinitionDto(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        datasheet_def_id=src.datasheet_def_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_int_field_config_from_dto(
    src: IntFieldConfigDto, mapper: Mapper
) -> IntFieldConfig:
    return IntFieldConfig(unit=src.unit)


def map_int_field_config_to_dto(
    src: IntFieldConfig, mapper: Mapper
) -> IntFieldConfigDto:
    return IntFieldConfigDto(unit=src.unit)


def map_decimal_field_config_from_dto(
    src: DecimalFieldConfigDto, mapper: Mapper
) -> DecimalFieldConfig:
    return DecimalFieldConfig(unit=src.unit, precision=src.precision)


def map_decimal_field_config_to_dto(
    src: DecimalFieldConfig, mapper: Mapper
) -> DecimalFieldConfigDto:
    return DecimalFieldConfigDto(unit=src.unit, precision=src.precision)


def map_string_field_config_from_dto(
    src: StringFieldConfigDto, mapper: Mapper
) -> StringFieldConfig:
    return StringFieldConfig(transforms=src.transforms)


def map_string_field_config_to_dto(
    src: StringFieldConfig, mapper: Mapper
) -> StringFieldConfigDto:
    return StringFieldConfigDto(transforms=src.transforms)


def map_bool_field_config_from_dto(
    src: BoolFieldConfigDto, mapper: Mapper
) -> BoolFieldConfig:
    return BoolFieldConfig(is_checkbox=src.is_checkbox)


def map_bool_field_config_to_dto(
    src: BoolFieldConfig, mapper: Mapper
) -> BoolFieldConfigDto:
    return BoolFieldConfigDto(is_checkbox=src.is_checkbox)


def map_static_choice_field_config_from_dto(
    src: StaticChoiceFieldConfigDto, mapper: Mapper
) -> StaticChoiceFieldConfig:
    return StaticChoiceFieldConfig(
        options=[
            StaticChoiceOption(
                id=option.id, label=option.label, help_text=option.help_text
            )
            for option in src.options
        ]
    )


def map_static_choice_field_config_to_dto(
    src: StaticChoiceFieldConfig, mapper: Mapper
) -> StaticChoiceFieldConfigDto:
    return StaticChoiceFieldConfigDto(
        options=[
            StaticChoiceOptionDto(
                id=option.id, label=option.label, help_text=option.help_text
            )
            for option in src.options
        ]
    )


def map_collapsible_node_field_config_from_dto(
    src: CollapsibleContainerFieldConfigDto, mapper: Mapper
) -> CollapsibleContainerFieldConfig:
    return CollapsibleContainerFieldConfig(is_collapsible=src.is_collapsible)


def map_collapsible_node_field_config_to_dto(
    src: CollapsibleContainerFieldConfig, mapper: Mapper
) -> CollapsibleContainerFieldConfigDto:
    return CollapsibleContainerFieldConfigDto(is_collapsible=src.is_collapsible)


def map_field_update_input_from_dto(
    src: FieldUpdateInputDto, mapper: Mapper
) -> FieldUpdate:
    return FieldUpdate(
        node_id=src.node_id,
        value=mapper.map(src.value, ValueUnion, ValueUnionDto),
    )


def map_field_update_input_to_dto(
    src: FieldUpdate, mapper: Mapper
) -> FieldUpdateInputDto:
    return FieldUpdateInputDto(
        node_id=src.node_id,
        value=mapper.map(src.value, ValueUnionDto, ValueUnion),
    )


def map_translation_config_from_dto(
    src: TranslationConfigDto, mapper: Mapper
) -> TranslationConfig:
    return TranslationConfig(help_text_name=src.help_text_name, label=src.label)


def map_translation_config_to_dto(
    src: TranslationConfig, mapper: Mapper
) -> TranslationConfigDto:
    return TranslationConfigDto(help_text_name=src.help_text_name, label=src.label)


def map_trigger_from_dto(src: TriggerDto, mapper: Mapper) -> Trigger:
    return Trigger(
        action=TriggerAction[src.action],
        target_type_id=src.target_type_id,
        params=dict(src.params),
    )


def map_trigger_to_dto(src: Trigger, mapper: Mapper) -> TriggerDto:
    return TriggerDto(
        action=str(src.action.value),
        target_type_id=src.target_type_id,
        params=dict(src.params),
    )


def map_node_config_from_dto(src: NodeConfigDto, mapper: Mapper) -> NodeConfig:
    return NodeConfig(
        field_details=None
        if src.field_details is None
        else mapper.map(
            src.field_details, field_details_to_domain_map[type(src.field_details)]
        ),
        translations=mapper.map(src.translations, TranslationConfig),
        triggers=mapper.map_many(src.triggers, Trigger),
        value_validator=src.value_validator,
        meta=mapper.map(src.meta, NodeMetaConfig, NodeMetaConfigDto),
    )


def map_node_config_to_dto(src: NodeConfig, mapper: Mapper) -> NodeConfigDto:
    field_details_dto = (
        None
        if src.field_details is None
        else mapper.map(
            src.field_details, field_details_from_domain[type(src.field_details)]
        )
    )
    mapped_config = NodeConfigDto(
        field_details=field_details_dto,
        value_validator=src.value_validator,
        translations=mapper.map(src.translations, TranslationConfigDto),
        triggers=mapper.map_many(src.triggers, TriggerDto),
        meta=mapper.map(src.meta, NodeMetaConfigDto, NodeMetaConfig),
    )
    assert type(mapped_config.field_details) is type(
        field_details_dto
    ), "Union has change type of config"

    return mapped_config


def map_node_meta_config_from_dto(
    src: NodeMetaConfigDto, mapper: Mapper
) -> NodeMetaConfig:
    return NodeMetaConfig(is_visible=src.is_visible)


def map_node_meta_config_to_dto(
    src: NodeMetaConfig, mapper: Mapper
) -> NodeMetaConfigDto:
    return NodeMetaConfigDto(is_visible=src.is_visible)


def map_project_definition_node_from_dto(
    src: ProjectDefinitionNodeDto, mapper: Mapper
) -> ProjectDefinitionNode:
    return ProjectDefinitionNode(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        config=mapper.map(src.config, NodeConfig),
        default_value=mapper.map(src.default_value, ValueUnion, ValueUnionDto),
        path=src.path,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_project_definition_node_to_dto(
    src: ProjectDefinitionNode, mapper: Mapper
) -> ProjectDefinitionNodeDto:
    return ProjectDefinitionNodeDto(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        config=mapper.map(src.config, NodeConfigDto),
        path=src.path,
        default_value=mapper.map(src.default_value, ValueUnionDto, ValueUnion),
    )


def map_project_definition_node_page_to_dto(
    src: Page[ProjectDefinitionNode], mapper: Mapper
) -> ProjectDefinitionNodePageDto:
    return ProjectDefinitionNodePageDto(
        next_page_token=src.next_page_token,
        limit=src.limit,
        results=mapper.map_many(
            src.results, ProjectDefinitionNodeDto, ProjectDefinitionNode
        ),
    )


def map_project_definition_tree_node_to_dto(
    src: ProjectDefinitionTreeNode, mapper: Mapper
) -> ProjectDefinitionTreeNodeDto:
    return ProjectDefinitionTreeNodeDto(
        definition=mapper.map(src.definition, ProjectDefinitionNodeDto),
        children=mapper.map_many(src.children, ProjectDefinitionTreeNodeDto),
    )


def map_project_definition_tree_to_dto(
    src: ProjectDefinitionNodeTree, mapper: Mapper
) -> ProjectDefinitionNodeTreeDto:
    return ProjectDefinitionNodeTreeDto(
        roots=mapper.map_many(src.roots, ProjectDefinitionTreeNodeDto)
    )


def map_project_input_from_dto(
    src: ProjectDetailsInputDto, mapper: Mapper
) -> ProjectDetails:
    return ProjectDetails(
        id=src.id,
        name=src.name,
        is_staged=False,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_project_from_dto(src: ProjectDetailsDto, mapper: Mapper) -> ProjectDetails:
    return ProjectDetails(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_project_to_dto(src: ProjectDetails, mapper: Mapper) -> ProjectDetailsDto:
    return ProjectDetailsDto(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_string_field_value_from_dto(src: StringFieldValueDto, mapper: Mapper) -> str:
    return src.text


def map_string_field_value_to_dto(src: str, mapper: Mapper) -> StringFieldValueDto:
    return StringFieldValueDto(text=src)


def map_bool_field_value_from_dto(src: BoolFieldValueDto, mapper: Mapper) -> bool:
    return src.enabled


def map_bool_field_value_to_dto(src: bool, mapper: Mapper) -> BoolFieldValueDto:
    return BoolFieldValueDto(enabled=src)


def map_int_field_value_from_dto(src: IntFieldValueDto, mapper: Mapper) -> int:
    return src.integer


def map_int_field_value_to_dto(src: int, mapper: Mapper) -> IntFieldValueDto:
    return IntFieldValueDto(integer=src)


def map_decimal_field_value_from_dto(
    src: DecimalFieldValueDto, mapper: Mapper
) -> float:
    return src.integer


def map_decimal_field_value_to_dto(src: float, mapper: Mapper) -> DecimalFieldValueDto:
    return DecimalFieldValueDto(integer=src)


def map_value_union_from_dto(src: ValueUnionDto, mapper: Mapper) -> ValueUnion:
    value = None

    if isinstance(src, StringFieldValueDto):
        value = src.text
    elif isinstance(src, BoolFieldValueDto):
        value = src.enabled
    elif isinstance(src, IntFieldValueDto):
        value = src.integer
    elif isinstance(src, DecimalFieldValueDto):
        value = src.numeric
    elif not src is None:
        raise LookupError(f"Field type not found {type(src)}")

    return value


def map_value_union_to_dto(src: ValueUnion, mapper: Mapper) -> ValueUnionDto:
    value = None

    if src is True or src is False:
        value = BoolFieldValueDto(enabled=src)
    elif isinstance(src, int):
        value = IntFieldValueDto(integer=src)
    elif isinstance(src, float):
        value = DecimalFieldValueDto(numeric=src)
    elif isinstance(src, str):
        value = StringFieldValueDto(text=src)
    elif not src is None:
        raise LookupError("Field type not found")

    return value


def map_project_node_from_dto(src: ProjectNodeDto, mapper: Mapper) -> ProjectNode:
    return ProjectNode(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        type_name=src.type_name,
        type_path=src.type_path,
        path=src.path,
        value=mapper.map(src.value, ValueUnion, ValueUnionDto),
        label=src.label,
    )


def map_project_node_to_dto(src: ProjectNode, mapper: Mapper) -> ProjectNodeDto:
    value = mapper.map(src.value, ValueUnionDto, ValueUnion)
    result = ProjectNodeDto(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        type_name=src.type_name,
        type_path=src.type_path,
        path=src.path,
        value=value,
        label=src.label,
    )

    assert type(result.value) is type(value), "Union has change type of config"
    return result


def map_project_node_meta_state_to_dto(
    src: ProjectNodeMetaState, mapper: Mapper
) -> ProjectNodeMetaStateDto:
    return ProjectNodeMetaStateDto(
        is_visible=src.is_visible, selected_child=src.selected_child
    )


def map_project_node_meta_to_dto(
    src: ProjectNodeMeta, mapper: Mapper
) -> ProjectNodeMetaDto:
    return ProjectNodeMetaDto(
        project_id=src.project_id,
        type_id=src.type_id,
        state=mapper.map(src.state, ProjectNodeMetaStateDto),
        definition=mapper.map(src.definition, ProjectDefinitionNodeDto),
    )


def map_project_node_tree_node_to_dto(
    src: ProjectNodeTreeNode, mapper: Mapper
) -> ProjectNodeTreeNodeDto:
    return ProjectNodeTreeNodeDto(
        node=mapper.map(src.node, ProjectNodeDto),
        children=mapper.map_many(src.children, ProjectNodeTreeTypeNodeDto),
    )


def map_project_node_tree_type_node_to_dto(
    src: ProjectNodeTreeTypeNode, mapper: Mapper
) -> ProjectNodeTreeTypeNodeDto:
    return ProjectNodeTreeTypeNodeDto(
        definition=mapper.map(src.definition, ProjectDefinitionNodeDto),
        state=mapper.map(src.state, ProjectNodeMetaStateDto),
        nodes=mapper.map_many(src.nodes, ProjectNodeTreeNodeDto),
    )


def map_project_node_tree_to_dto(
    src: ProjectNodeTree, mapper: Mapper
) -> ProjectNodeTreeDto:
    return ProjectNodeTreeDto(
        roots=mapper.map_many(src.roots, ProjectNodeTreeTypeNodeDto)
    )


def map_translation_input_from_dto(
    src: TranslationInputDto, mapper: Mapper
) -> Translation:
    return Translation(
        id=src.id,
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        scope=src.scope,
        value=src.value,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_translation_from_dto(src: TranslationDto, mapper: Mapper) -> Translation:
    return Translation(
        id=src.id,
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        scope=src.scope,
        value=src.value,
        creation_date_utc=src.creation_date_utc,
    )


def map_translation_to_dto(src: Translation, mapper: Mapper) -> TranslationDto:
    return TranslationDto(
        id=src.id,
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        scope=src.scope,
        value=src.value,
        creation_date_utc=src.creation_date_utc,
    )


def map_translation_id_from_dto(src: TranslationIdDto, mapper: Mapper) -> TranslationId:
    return TranslationId(
        ressource_id=src.ressource_id,
        locale=src.locale,
        scope=src.scope,
        name=src.name,
    )


def map_translation_id_to_dto(src: TranslationId, mapper: Mapper) -> TranslationIdDto:
    return TranslationDto(
        ressource_id=src.ressource_id,
        locale=src.locale,
        scope=src.scope,
        name=src.name,
    )


def map_input_formula_expression_from_dto(
    src: InputFormulaDto, mapper: Mapper
) -> FormulaExpression:
    return FormulaExpression(
        id=src.id,
        project_def_id=src.project_def_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
    )


def map_formula_expression_to_dto(
    src: FormulaExpression, mapper: Mapper
) -> FormulaExpressionDto:
    return FormulaExpressionDto(
        id=src.id,
        project_def_id=src.project_def_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
    )


def map_formula_expression_from_dto(
    src: FormulaExpressionDto, mapper: Mapper
) -> FormulaExpression:
    return FormulaExpression(
        id=src.id,
        project_def_id=src.project_def_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
    )


def map_formula_to_expression_dto(src: Formula, mapper: Mapper) -> FormulaExpressionDto:
    return FormulaExpressionDto(
        id=src.id,
        project_def_id=src.project_def_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
    )


def map_datasheet_definition_to_dto(
    src: DatasheetDefinition, mapper: Mapper
) -> DatasheetDefinitionDto:
    return DatasheetDefinitionDto(
        id=src.id,
        name=src.name,
        properties={
            key: ElementPropertySchemaDto(value_validator=value.value_validator)
            for key, value in src.properties.items()
        },
    )


def map_datasheet_definition_from_dto(
    src: DatasheetDefinitionDto, mapper: Mapper
) -> DatasheetDefinition:
    return DatasheetDefinition(
        id=src.id,
        name=src.name,
        properties={
            key: ElementPropertySchema(value_validator=value.value_validator)
            for key, value in src.properties.items()
        },
    )


def map_datasheet_definition_element_to_dto(
    src: DatasheetDefinitionElement, mapper: Mapper
) -> DatasheetDefinitionElementDto:
    return DatasheetDefinitionElementDto(
        id=src.id,
        unit_id=src.unit_id,
        is_collection=src.is_collection,
        name=src.name,
        datasheet_def_id=src.datasheet_def_id,
        order_index=src.order_index,
        default_properties={
            name: DatasheetDefinitionElementPropertyDto(
                is_readonly=property_details.is_readonly,
                value=property_details.value,
            )
            for (name, property_details) in src.default_properties.items()
        },
        tags=src.tags,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_definition_element_from_dto(
    src: DatasheetDefinitionElementDto, mapper: Mapper
) -> DatasheetDefinitionElement:
    return DatasheetDefinitionElement(
        id=src.id,
        unit_id=src.unit_id,
        name=src.name,
        is_collection=src.is_collection,
        datasheet_def_id=src.datasheet_def_id,
        order_index=src.order_index,
        default_properties={
            name: DatasheetDefinitionElementProperty(
                is_readonly=property_details.is_readonly,
                value=property_details.value,
            )
            for (name, property_details) in src.default_properties.items()
        },
        tags=src.tags,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


label_attribute_schema_union_dto_mapping = RevervibleUnionMapping(
    LabelAttributeSchemaDtoUnion,
    LabelAttributeSchemaUnion,
    {
        StaticPropertyDto: StaticProperty,
        CollectionAggregateDto: CollectionAggregate,
        DatasheetAggregateDto: DatasheetAggregate,
        FormulaAggregateDto: FormulaAggregate,
    },
)


def map_label_collection_from_dto(
    src: LabelCollectionDto, mapper: Mapper
) -> LabelCollection:
    return LabelCollection(
        id=src.id,
        datasheet_definition_id=src.datasheet_definition_id,
        name=src.name,
        attributes_schema=mapper.map_dict_values(
            src.attributes_schema, label_attribute_schema_union_dto_mapping.from_origin
        ),
    )


def map_label_collection_to_dto(
    src: LabelCollection, mapper: Mapper
) -> LabelCollectionDto:
    return LabelCollectionDto(
        id=src.id,
        datasheet_definition_id=src.datasheet_definition_id,
        name=src.name,
        attributes_schema=mapper.map_dict_values(
            src.attributes_schema, label_attribute_schema_union_dto_mapping.to_origin
        ),
    )


label_attribute_value_dto_mappings = RevervibleUnionMapping(
    LabelAttributeValueDto,
    LabelAttributeUnion,
    {
        BoolFieldValueDto: bool,
        IntFieldValueDto: int,
        StringFieldValueDto: str,
        DecimalFieldValueDto: float,
        ReferenceIdDto: UUID,
    },
)


def map_datasheet_definition_label_from_dto(src: LabelDto, mapper: Mapper) -> Label:
    return Label(
        id=src.id,
        label_collection_id=src.label_collection_id,
        order_index=src.order_index,
        attributes=mapper.map_dict_values(
            src.attributes, label_attribute_value_dto_mappings.from_origin
        ),
    )


def map_datasheet_definition_label_to_dto(src: Label, mapper: Mapper) -> LabelDto:
    return LabelDto(
        id=src.id,
        label_collection_id=src.label_collection_id,
        order_index=src.order_index,
        attributes=mapper.map_dict_values(
            src.attributes, label_attribute_value_dto_mappings.to_origin
        ),
    )


def map_new_datasheet_from_dto(src: NewDatasheetDto, mapper: Mapper) -> Datasheet:
    datasheet_id = uuid4()
    return Datasheet(
        id=datasheet_id,
        name=src.name,
        is_staged=src.is_staged,
        datasheet_def_id=src.datasheet_definition_id,
        from_datasheet_id=datasheet_id
        if src.from_datasheet_id is None
        else src.from_datasheet_id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_datasheet_import_from_dto(src: DatasheetImportDto, mapper: Mapper) -> Datasheet:
    return Datasheet(
        id=src.id,
        name=src.name,
        is_staged=False,
        datasheet_def_id=src.datasheet_definition_id,
        from_datasheet_id=src.id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_datasheet_to_dto(src: Datasheet, mapper: Mapper) -> DatasheetDto:
    return DatasheetDto(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        datasheet_def_id=src.datasheet_def_id,
        from_datasheet_id=src.from_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_page_element_to_dto(
    src: Page[DatasheetElement], mapper: Mapper
) -> DatasheetElementPageDto:
    return DatasheetElementPageDto(
        next_page_token=src.next_page_token,
        limit=src.limit,
        results=mapper.map_many(src.results, DatasheetElementDto, DatasheetElement),
    )


def map_datasheet_element_import_from_dto(
    src: DatasheetElementImportDto, mapper: Mapper
) -> DatasheetElement:
    return DatasheetElement(
        datasheet_id=src.datasheet_id,
        element_def_id=src.element_def_id,
        child_element_reference=src.child_element_reference,
        properties=src.properties,
        original_datasheet_id=src.original_datasheet_id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_datasheet_element_to_dto(
    src: DatasheetElement, mapper: Mapper
) -> DatasheetElementDto:
    return DatasheetElementDto(
        datasheet_id=src.datasheet_id,
        element_def_id=src.element_def_id,
        child_element_reference=src.child_element_reference,
        properties=src.properties,
        original_datasheet_id=src.original_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_from_dto(
    src: DatasheetElementDto, mapper: Mapper
) -> DatasheetElement:
    return DatasheetElement(
        datasheet_id=src.datasheet_id,
        element_def_id=src.element_def_id,
        child_element_reference=src.child_element_reference,
        properties=src.properties,
        original_datasheet_id=src.original_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_clone_target_from_dto(
    src: DatasheetCloneTargetDto, mapper: Mapper
) -> DatasheetCloneTarget:
    return DatasheetCloneTarget(
        target_datasheet_id=src.target_datasheet_id, new_name=src.new_name
    )

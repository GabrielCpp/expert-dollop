from uuid import UUID, uuid4
from typing import List
from decimal import Decimal
from expert_dollup.shared.starlette_injection import Clock, IdProvider
from expert_dollup.shared.automapping import Mapper, RevervibleUnionMapping
from expert_dollup.shared.database_services import Page
from expert_dollup.app.dtos import *
from expert_dollup.core.domains import *
from expert_dollup.core.units.node_value_validation import make_schema

primitive_with_none_union_dto_mappings = RevervibleUnionMapping(
    PrimitiveWithNoneUnionDto,
    PrimitiveWithNoneUnion,
    {
        BoolFieldValueDto: bool,
        IntFieldValueDto: int,
        StringFieldValueDto: str,
        DecimalFieldValueDto: Decimal,
        type(None): type(None),
    },
)

primitive_union_dto_mappings = RevervibleUnionMapping(
    PrimitiveUnionDto,
    PrimitiveUnion,
    {
        BoolFieldValueDto: bool,
        IntFieldValueDto: int,
        StringFieldValueDto: str,
        DecimalFieldValueDto: Decimal,
    },
)

primitive_with_reference_union_dto_mappings = RevervibleUnionMapping(
    PrimitiveWithReferenceUnionDto,
    PrimitiveWithReferenceUnion,
    {
        BoolFieldValueDto: bool,
        IntFieldValueDto: int,
        StringFieldValueDto: str,
        DecimalFieldValueDto: Decimal,
        ReferenceIdDto: UUID,
    },
)


def map_project_definition_from_dto(
    src: ProjectDefinitionDto, mapper: Mapper
) -> ProjectDefinition:
    return ProjectDefinition(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        properties={
            key: ElementPropertySchema(value_validator=value.value_validator)
            for key, value in src.properties.items()
        },
        creation_date_utc=src.creation_date_utc,
    )


def map_project_definition_to_dto(
    src: ProjectDefinition, mapper: Mapper
) -> ProjectDefinitionDto:
    return ProjectDefinitionDto(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        properties={
            key: ElementPropertySchemaDto(value_validator=value.value_validator)
            for key, value in src.properties.items()
        },
        creation_date_utc=src.creation_date_utc,
    )


def map_int_field_config_from_dto(
    src: IntFieldConfigDto, mapper: Mapper
) -> IntFieldConfig:
    return IntFieldConfig(unit=src.unit, default_value=src.integer)


def map_int_field_config_to_dto(
    src: IntFieldConfig, mapper: Mapper
) -> IntFieldConfigDto:
    return IntFieldConfigDto(unit=src.unit, integer=src.default_value)


def map_decimal_field_config_from_dto(
    src: DecimalFieldConfigDto, mapper: Mapper
) -> DecimalFieldConfig:
    return DecimalFieldConfig(
        unit=src.unit, precision=src.precision, default_value=src.numeric
    )


def map_decimal_field_config_to_dto(
    src: DecimalFieldConfig, mapper: Mapper
) -> DecimalFieldConfigDto:
    return DecimalFieldConfigDto(
        unit=src.unit, precision=src.precision, numeric=src.default_value
    )


def map_string_field_config_from_dto(
    src: StringFieldConfigDto, mapper: Mapper
) -> StringFieldConfig:
    return StringFieldConfig(transforms=src.transforms, default_value=src.text)


def map_string_field_config_to_dto(
    src: StringFieldConfig, mapper: Mapper
) -> StringFieldConfigDto:
    return StringFieldConfigDto(transforms=src.transforms, text=src.default_value)


def map_bool_field_config_from_dto(
    src: BoolFieldConfigDto, mapper: Mapper
) -> BoolFieldConfig:
    return BoolFieldConfig(default_value=src.enabled)


def map_bool_field_config_to_dto(
    src: BoolFieldConfig, mapper: Mapper
) -> BoolFieldConfigDto:
    return BoolFieldConfigDto(enabled=src.default_value)


def map_static_choice_field_config_from_dto(
    src: StaticChoiceFieldConfigDto, mapper: Mapper
) -> StaticChoiceFieldConfig:
    return StaticChoiceFieldConfig(
        options=[
            StaticChoiceOption(
                id=option.id, label=option.label, help_text=option.help_text
            )
            for option in src.options
        ],
        default_value=src.selected,
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
        ],
        selected=src.default_value,
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
        value=mapper.map(src.value, primitive_with_none_union_dto_mappings.from_origin),
    )


def map_field_update_input_to_dto(
    src: FieldUpdate, mapper: Mapper
) -> FieldUpdateInputDto:
    return FieldUpdateInputDto(
        node_id=src.node_id,
        value=mapper.map(src.value, primitive_with_none_union_dto_mappings.to_origin),
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


field_details_union_dto_mappings = RevervibleUnionMapping(
    FieldDetailsUnionDto,
    FieldDetailsUnion,
    field_details_to_domain_map,
)


def map_collapsible_container_field_config_from_dto(
    src: CollapsibleContainerFieldConfigDto, mapper: Mapper
) -> CollapsibleContainerFieldConfig:
    return CollapsibleContainerFieldConfig(is_collapsible=src.is_collapsible)


def map_collapsible_container_field_config_to_dto(
    src: CollapsibleContainerFieldConfig, mapper: Mapper
) -> CollapsibleContainerFieldConfigDto:
    return CollapsibleContainerFieldConfigDto(is_collapsible=src.is_collapsible)


def map_static_number_field_config_from_dto(
    src: StaticNumberFieldConfigDto, mapper: Mapper
) -> StaticNumberFieldConfig:
    return StaticNumberFieldConfig(
        pass_to_translation=src.pass_to_translation,
        precision=src.precision,
        unit=src.unit,
    )


def map_static_number_field_config_to_dto(
    src: StaticNumberFieldConfig, mapper: Mapper
) -> StaticNumberFieldConfigDto:
    return StaticNumberFieldConfigDto(
        pass_to_translation=src.pass_to_translation,
        precision=src.precision,
        unit=src.unit,
    )


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
        project_definition_id=src.project_definition_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        field_details=mapper.map(
            src.field_details, field_details_union_dto_mappings.from_origin
        ),
        translations=mapper.map(src.translations, TranslationConfig),
        triggers=mapper.map_many(src.triggers, Trigger),
        meta=mapper.map(src.meta, NodeMetaConfig, NodeMetaConfigDto),
        path=src.path,
        creation_date_utc=src.creation_date_utc,
    )


def map_project_definition_node_to_dto(
    src: ProjectDefinitionNode, mapper: Mapper
) -> ProjectDefinitionNodeDto:
    return ProjectDefinitionNodeDto(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        field_details=mapper.map(
            src.field_details, field_details_union_dto_mappings.to_origin
        ),
        translations=mapper.map(src.translations, TranslationConfigDto),
        triggers=mapper.map_many(src.triggers, TriggerDto),
        meta=mapper.map(src.meta, NodeMetaConfigDto, NodeMetaConfig),
        validator=make_schema(src),
        path=src.path,
        creation_date_utc=src.creation_date_utc,
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
        id=mapper.get(IdProvider).uuid4(),
        name=src.name,
        is_staged=False,
        project_definition_id=src.project_definition_id,
        datasheet_id=src.datasheet_id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_project_details_from_dto(
    src: ProjectDetailsDto, mapper: Mapper
) -> ProjectDetails:
    return ProjectDetails(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_definition_id=src.project_definition_id,
        datasheet_id=src.datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_project_details_to_dto(
    src: ProjectDetails, mapper: Mapper
) -> ProjectDetailsDto:
    return ProjectDetailsDto(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_definition_id=src.project_definition_id,
        datasheet_id=src.datasheet_id,
        creation_date_utc=src.creation_date_utc,
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
) -> Decimal:
    return src.numeric


def map_decimal_field_value_to_dto(
    src: Decimal, mapper: Mapper
) -> DecimalFieldValueDto:
    return DecimalFieldValueDto(numeric=src)


def map_reference_id_from_dto(src: ReferenceIdDto, mapper: Mapper) -> UUID:
    return src.uuid


def map_reference_id_to_dto(src: UUID, mapper: Mapper) -> ReferenceIdDto:
    return ReferenceIdDto(uuid=src)


def map_project_node_from_dto(src: ProjectNodeDto, mapper: Mapper) -> ProjectNode:
    return ProjectNode(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        type_name=src.type_name,
        type_path=src.type_path,
        path=src.path,
        value=mapper.map(src.value, primitive_with_none_union_dto_mappings.from_origin),
        label=src.label,
    )


def map_project_node_to_dto(src: ProjectNode, mapper: Mapper) -> ProjectNodeDto:
    value = mapper.map(src.value, primitive_with_none_union_dto_mappings.to_origin)
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
        project_definition_id=src.project_definition_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
    )


def map_formula_expression_to_dto(
    src: FormulaExpression, mapper: Mapper
) -> FormulaExpressionDto:
    return FormulaExpressionDto(
        id=src.id,
        project_definition_id=src.project_definition_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
    )


def map_formula_expression_from_dto(
    src: FormulaExpressionDto, mapper: Mapper
) -> FormulaExpression:
    return FormulaExpression(
        id=src.id,
        project_definition_id=src.project_definition_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
    )


def map_formula_to_expression_dto(src: Formula, mapper: Mapper) -> FormulaExpressionDto:
    return FormulaExpressionDto(
        id=src.id,
        project_definition_id=src.project_definition_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
    )


def map_datasheet_definition_element_to_dto(
    src: DatasheetDefinitionElement, mapper: Mapper
) -> DatasheetDefinitionElementDto:
    return DatasheetDefinitionElementDto(
        id=src.id,
        unit_id=src.unit_id,
        is_collection=src.is_collection,
        name=src.name,
        project_definition_id=src.project_definition_id,
        order_index=src.order_index,
        default_properties=mapper.map_dict_values(
            src.default_properties, DatasheetDefinitionElementPropertyDto
        ),
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
        project_definition_id=src.project_definition_id,
        order_index=src.order_index,
        default_properties=mapper.map_dict_values(
            src.default_properties, DatasheetDefinitionElementProperty
        ),
        tags=src.tags,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_definition_element_property_from_dto(
    src: DatasheetDefinitionElementPropertyDto, mapper: Mapper
) -> DatasheetDefinitionElementProperty:
    return DatasheetDefinitionElementProperty(
        is_readonly=src.is_readonly,
        value=mapper.map(src.value, primitive_union_dto_mappings.from_origin),
    )


def map_datasheet_definition_element_property_to_dto(
    src: DatasheetDefinitionElementProperty, mapper: Mapper
) -> DatasheetDefinitionElementPropertyDto:
    return DatasheetDefinitionElementPropertyDto(
        is_readonly=src.is_readonly,
        value=mapper.map(src.value, primitive_union_dto_mappings.to_origin),
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
        project_definition_id=src.project_definition_id,
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
        project_definition_id=src.project_definition_id,
        name=src.name,
        attributes_schema=mapper.map_dict_values(
            src.attributes_schema, label_attribute_schema_union_dto_mapping.to_origin
        ),
    )


def map_static_property_from_dto(
    src: StaticPropertyDto, mapper: Mapper
) -> StaticProperty:
    return StaticProperty(json_schema=src.json_schema)


def map_static_property_to_dto(
    src: StaticProperty, mapper: Mapper
) -> StaticPropertyDto:
    return StaticPropertyDto(json_schema=src.json_schema)


def map_collection_aggregate_from_dto(
    src: CollectionAggregateDto, mapper: Mapper
) -> CollectionAggregate:
    return CollectionAggregate(from_collection=src.from_collection)


def map_collection_aggregate_to_dto(
    src: CollectionAggregate, mapper: Mapper
) -> CollectionAggregateDto:
    return CollectionAggregateDto(from_collection=src.from_collection)


def map_datasheet_aggregate_from_dto(
    src: DatasheetAggregateDto, mapper: Mapper
) -> DatasheetAggregate:
    return DatasheetAggregate(from_datasheet=src.from_datasheet)


def map_datasheet_aggregate_to_dto(
    src: DatasheetAggregate, mapper: Mapper
) -> DatasheetAggregateDto:
    return DatasheetAggregateDto(from_datasheet=src.from_datasheet)


def map_formula_aggregate_from_dto(
    src: FormulaAggregateDto, mapper: Mapper
) -> FormulaAggregate:
    return FormulaAggregate(from_formula=src.from_formula)


def map_formula_aggregate_to_dto(
    src: FormulaAggregate, mapper: Mapper
) -> FormulaAggregateDto:
    return FormulaAggregateDto(from_formula=src.from_formula)


label_attribute_value_dto_mappings = RevervibleUnionMapping(
    LabelAttributeValueDto,
    LabelAttributeUnion,
    {
        BoolFieldValueDto: bool,
        IntFieldValueDto: int,
        StringFieldValueDto: str,
        DecimalFieldValueDto: Decimal,
        ReferenceIdDto: UUID,
    },
)


def map_datasheet_definition_label_from_dto(src: LabelDto, mapper: Mapper) -> Label:
    return Label(
        id=src.id,
        name=src.name,
        label_collection_id=src.label_collection_id,
        order_index=src.order_index,
        attributes=mapper.map_dict_values(
            src.attributes, label_attribute_value_dto_mappings.from_origin
        ),
    )


def map_datasheet_definition_label_to_dto(src: Label, mapper: Mapper) -> LabelDto:
    return LabelDto(
        id=src.id,
        name=src.name,
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
        project_definition_id=src.project_definition_id,
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
        project_definition_id=src.project_definition_id,
        from_datasheet_id=src.id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_datasheet_to_dto(src: Datasheet, mapper: Mapper) -> DatasheetDto:
    return DatasheetDto(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_definition_id=src.project_definition_id,
        from_datasheet_id=src.from_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_import_from_dto(
    src: DatasheetElementImportDto, mapper: Mapper
) -> DatasheetElement:
    return DatasheetElement(
        datasheet_id=src.datasheet_id,
        element_def_id=src.element_def_id,
        child_element_reference=src.child_element_reference,
        properties=mapper.map_dict_values(
            src.properties, primitive_union_dto_mappings.from_origin
        ),
        ordinal=0,
        original_datasheet_id=src.original_datasheet_id,
        original_owner_organization_id=src.original_owner_organization_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_to_dto(
    src: DatasheetElement, mapper: Mapper
) -> DatasheetElementDto:
    return DatasheetElementDto(
        datasheet_id=src.datasheet_id,
        element_def_id=src.element_def_id,
        child_element_reference=src.child_element_reference,
        properties=mapper.map_dict_values(
            src.properties, primitive_union_dto_mappings.to_origin
        ),
        original_datasheet_id=src.original_datasheet_id,
        original_owner_organization_id=src.original_owner_organization_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_from_dto(
    src: DatasheetElementDto, mapper: Mapper
) -> DatasheetElement:
    return DatasheetElement(
        datasheet_id=src.datasheet_id,
        element_def_id=src.element_def_id,
        child_element_reference=src.child_element_reference,
        original_owner_organization_id=src.original_owner_organization_id,
        properties=mapper.map_dict_values(
            src.properties, primitive_union_dto_mappings.from_origin
        ),
        original_datasheet_id=src.original_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_clone_target_from_dto(
    src: DatasheetCloneTargetDto, mapper: Mapper
) -> DatasheetCloneTarget:
    return DatasheetCloneTarget(
        target_datasheet_id=src.target_datasheet_id, new_name=src.new_name
    )


def map_measure_unit_from_dto(src: MeasureUnitDto, mapper: Mapper) -> MeasureUnit:
    return MeasureUnit(id=src.id)


def map_measure_unit_to_dto(src: MeasureUnit, mapper: Mapper) -> MeasureUnitDto:
    return MeasureUnitDto(id=src.id)


def map_report_definition_from_dto(
    src: ReportDefinitionDto, mapper: Mapper
) -> ReportDefinition:
    return ReportDefinition(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        structure=mapper.map(src.structure, ReportStructure),
        distributable=src.distributable,
    )


def map_report_definition_to_dto(
    src: ReportDefinition, mapper: Mapper
) -> ReportDefinitionDto:
    return ReportDefinitionDto(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        structure=mapper.map(src.structure, ReportStructureDto),
        distributable=src.distributable,
    )


def map_report_structure_from_dto(
    src: ReportStructureDto, mapper: Mapper
) -> ReportStructure:
    return ReportStructure(
        datasheet_selection_alias=src.datasheet_selection_alias,
        formula_attribute=mapper.map(src.formula_attribute, AttributeBucket),
        datasheet_attribute=mapper.map(src.datasheet_attribute, AttributeBucket),
        stage_summary=mapper.map(src.stage_summary, StageSummary),
        report_summary=mapper.map_many(src.report_summary, ReportComputation),
        joins_cache=mapper.map_many(src.joins_cache, ReportJoin),
        columns=mapper.map_many(src.columns, ReportComputation),
        group_by=mapper.map_many(src.group_by, AttributeBucket),
        order_by=mapper.map_many(src.order_by, AttributeBucket),
    )


def map_report_structure_to_dto(
    src: ReportStructure, mapper: Mapper
) -> ReportStructureDto:
    return ReportStructureDto(
        datasheet_selection_alias=src.datasheet_selection_alias,
        formula_attribute=mapper.map(src.formula_attribute, AttributeBucketDto),
        datasheet_attribute=mapper.map(src.datasheet_attribute, AttributeBucketDto),
        stage_summary=mapper.map(src.stage_summary, StageSummaryDto),
        report_summary=mapper.map_many(src.report_summary, ReportComputationDto),
        joins_cache=mapper.map_many(src.joins_cache, ReportJoinDto),
        columns=mapper.map_many(src.columns, ReportComputationDto),
        group_by=mapper.map_many(src.group_by, AttributeBucketDto),
        order_by=mapper.map_many(src.order_by, AttributeBucketDto),
    )


def map_stage_grouping_to_dto(src: StageSummary, mapper: Mapper) -> StageSummaryDto:
    return StageSummaryDto(
        label=mapper.map(src.label, AttributeBucketDto),
        summary=mapper.map(src.summary, ReportComputationDto),
    )


def map_stage_grouping_from_dto(src: StageSummaryDto, mapper: Mapper) -> StageSummary:
    return StageSummary(
        label=mapper.map(src.label, AttributeBucket),
        summary=mapper.map(src.summary, ReportComputation),
    )


def map_report_computation_to_dto(
    src: ReportComputation, mapper: Mapper
) -> ReportComputationDto:
    return ReportComputationDto(
        name=src.name,
        is_visible=src.is_visible,
        expression=src.expression,
        unit=mapper.map(src.unit, AttributeBucketDto)
        if isinstance(src.unit, AttributeBucket)
        else src.unit,
    )


def map_report_computation_from_dto(
    src: ReportComputationDto, mapper: Mapper
) -> ReportComputation:
    return ReportComputation(
        name=src.name,
        is_visible=src.is_visible,
        expression=src.expression,
        unit=mapper.map(src.unit, AttributeBucket)
        if isinstance(src.unit, AttributeBucketDto)
        else src.unit,
    )


def map_attribute_bucket_from_dto(
    src: AttributeBucketDto, mapper: Mapper
) -> AttributeBucket:
    return AttributeBucket(
        bucket_name=src.bucket_name, attribute_name=src.attribute_name
    )


def map_attribute_bucket_to_dto(
    src: AttributeBucket, mapper: Mapper
) -> AttributeBucketDto:
    return AttributeBucketDto(
        bucket_name=src.bucket_name, attribute_name=src.attribute_name
    )


def map_report_join_from_dto(src: ReportJoinDto, mapper: Mapper) -> ReportJoin:
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


def map_report_join_to_dto(src: ReportJoin, mapper: Mapper) -> ReportJoinDto:
    return ReportJoinDto(
        from_object_name=src.from_object_name,
        from_property_name=src.from_property_name,
        join_on_collection=src.join_on_collection,
        join_on_attribute=src.join_on_attribute,
        alias_name=src.alias_name,
        warn_about_idle_items=src.warn_about_idle_items,
        same_cardinality=src.same_cardinality,
        allow_dicard_element=src.allow_dicard_element,
    )


def map_report_row_to_dto(src: ReportRow, mapper: Mapper) -> ReportRowDto:
    return ReportRowDto(
        node_id=src.node_id,
        formula_id=src.formula_id,
        element_def_id=src.element_def_id,
        child_reference_id=src.child_reference_id,
        columns=mapper.map_many(src.columns, ComputedValueDto),
        row={
            name: {
                att_name: mapper.map_many(value, ReferenceIdDto)
                if isinstance(value, list)
                else mapper.map(
                    value, primitive_with_reference_union_dto_mappings.to_origin
                )
                for att_name, value in attributes.items()
            }
            for name, attributes in src.row.items()
        },
    )


def map_computed_value_to_dto(src: ComputedValue, mapper: Mapper) -> ComputedValueDto:
    return ComputedValueDto(
        label=src.label,
        value=mapper.map(src.value, primitive_union_dto_mappings.to_origin),
        unit=src.unit,
        is_visible=src.is_visible,
    )


def map_computed_value_from_dto(src: ComputedValueDto, mapper: Mapper) -> ComputedValue:
    return ComputedValue(
        label=src.label,
        value=mapper.map(src.value, primitive_union_dto_mappings.from_origin),
        unit=src.unit,
        is_visible=src.is_visible,
    )


def map_stage_column_to_dto(src: StageColumn, mapper: Mapper) -> StageColumnDto:
    return StageColumnDto(
        label=src.label,
        unit=src.unit,
        is_visible=src.is_visible,
    )


def map_stage_column_from_dto(src: StageColumnDto, mapper: Mapper) -> StageColumn:
    return StageColumn(
        label=src.label,
        unit=src.unit,
        is_visible=src.is_visible,
    )


def map_report_to_dto(src: Report, mapper: Mapper) -> ReportDto:
    return ReportDto(
        name=src.name,
        datasheet_id=src.datasheet_id,
        stages=mapper.map_many(src.stages, ReportStageDto),
        summaries=mapper.map_many(src.summaries, ComputedValueDto),
        creation_date_utc=src.creation_date_utc,
    )


def map_report_group_to_dto(src: ReportStage, mapper: Mapper) -> ReportStageDto:
    return ReportStageDto(
        summary=mapper.map(src.summary, ComputedValueDto),
        columns=mapper.map_many(src.columns, StageColumn),
        rows=mapper.map_many(src.rows, ReportRowDto),
    )


def map_primitive_with_none_union_to_dto(
    src: PrimitiveWithNoneUnion, mapper: Mapper
) -> PrimitiveWithNoneUnionDto:
    return mapper.map(src, primitive_with_none_union_dto_mappings.to_origin)


def map_primitive_with_none_union_from_dto(
    src: PrimitiveWithNoneUnionDto, mapper: Mapper
) -> PrimitiveWithNoneUnion:
    return mapper.map(src, primitive_with_none_union_dto_mappings.from_origin)


def map_translations_to_json_bundle(src: List[Translation], mapper: Mapper) -> dict:
    return {translation.name: translation.value for translation in src}


def map_minimal_report_dto(src: Report, mapper: Mapper) -> MinimalReportDto:
    return MinimalReportDto(
        name=src.name,
        stages=mapper.map_many(src.stages, MinimalReportStageDto),
        summaries=mapper.map_many(src.summaries, ComputedValueDto),
    )


def map_minimal_report_stage_dto(
    src: ReportStage, mapper: Mapper
) -> MinimalReportStageDto:
    return MinimalReportStageDto(
        summary=mapper.map(src.summary, ComputedValueDto),
        columns=mapper.map_many(src.columns, StageColumnDto),
        rows=mapper.map_many(src.rows, MinimalReportRowDto),
    )


def map_minimal_report_row_dto(src: ReportRow, mapper: Mapper) -> MinimalReportRowDto:
    return MinimalReportRowDto(
        node_id=src.node_id,
        formula_id=src.formula_id,
        element_def_id=src.element_def_id,
        child_reference_id=src.child_reference_id,
        columns=mapper.map_many(src.columns, ComputedValueDto),
    )


def map_user_to_dto(src: User, mapper: Mapper) -> UserDto:
    return UserDto(
        oauth_id=src.oauth_id,
        id=src.id,
        email=src.email,
        permissions=src.permissions,
        organization_id=src.organization_id,
    )


def map_organization_to_dto(src: Organization, mapper: Mapper) -> OrganizationDto:
    return OrganizationDto(
        id=src.id,
        name=src.name,
        email=src.email,
        limits=mapper.map(src.limits, OrganizationLimitsDto),
    )


def map_organization_limits_dto(
    src: OrganizationLimits, mapper: Mapper
) -> OrganizationLimitsDto:
    return OrganizationLimitsDto(
        active_project_count=src.active_project_count,
        active_project_overall_collection_count=src.active_project_overall_collection_count,
        active_datasheet_count=src.active_datasheet_count,
        active_datasheet_custom_element_count=src.active_datasheet_custom_element_count,
    )


def map_distributable_item_to_dto(
    src: DistributableItem, mapper: Mapper
) -> DistributableItemDto:
    return DistributableItemDto(
        id=src.id,
        project_id=src.project_id,
        report_definition_id=src.report_definition_id,
        node_id=src.node_id,
        formula_id=src.formula_id,
        supplied_item=mapper.map(src.supplied_item, SuppliedItemDto),
        distribution_ids=src.distribution_ids,
        summary=mapper.map(src.summary, ComputedValueDto),
        columns=mapper.map_many(src.columns, ComputedValueDto),
        obsolete=src.obsolete,
        creation_date_utc=src.creation_date_utc,
    )


def map_supplied_item_to_dto(src: SuppliedItem, mapper: Mapper) -> SuppliedItemDto:
    return SuppliedItemDto(
        datasheet_id=src.datasheet_id,
        element_def_id=src.element_def_id,
        child_reference_id=src.child_reference_id,
        organization_id=src.organization_id,
    )


def map_measure_unit_to_dto(src: MeasureUnit, mapper: Mapper) -> MeasureUnitDto:
    return MeasureUnitDto(id=src.id)

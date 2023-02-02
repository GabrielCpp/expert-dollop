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

field_details_union_dto_mappings = RevervibleUnionMapping(
    FieldDetailsUnionDto,
    FieldDetailsUnion,
    field_details_to_domain_map,
)


def map_project_definition_from_dto(
    src: ProjectDefinitionDto, mapper: Mapper
) -> ProjectDefinition:
    return ProjectDefinition(
        id=src.id,
        name=src.name,
        creation_date_utc=src.creation_date_utc,
    )


def map_project_definition_to_dto(
    src: ProjectDefinition, mapper: Mapper
) -> ProjectDefinitionDto:
    return ProjectDefinitionDto(
        id=src.id,
        name=src.name,
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
        ordinal=src.ordinal,
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
        ordinal=src.ordinal,
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


def map_field_translation_from_dto(
    src: FieldTranslationDto, mapper: Mapper
) -> FieldTranslation:
    return FieldTranslation(locale=src.locale, name=src.name, value=src.value)


def map_new_translation_from_dto(
    src: NewTranslationDto, mapper: Mapper
) -> NewTranslation:
    return NewTranslation(
        locale=src.locale,
        name=src.name,
        scope=src.scope,
        value=src.value,
    )


def map_translation_from_dto(src: TranslationDto, mapper: Mapper) -> Translation:
    return Translation(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        scope=src.scope,
        value=src.value,
        creation_date_utc=src.creation_date_utc,
    )


def map_translation_to_dto(src: Translation, mapper: Mapper) -> TranslationDto:
    return TranslationDto(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        scope=src.scope,
        value=src.value,
        creation_date_utc=src.creation_date_utc,
    )


def map_input_formula_expression_from_dto(
    src: InputFormulaDto, mapper: Mapper
) -> FormulaExpression:
    return FormulaExpression(
        id=src.id,
        project_definition_id=src.project_definition_id,
        attached_to_type_id=src.path[-1],
        name=src.name,
        expression=src.expression,
        path=src.path,
        creation_date_utc=mapper.get(Clock).utcnow(),
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
        path=src.path,
        creation_date_utc=src.creation_date_utc,
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
        path=src.path,
        creation_date_utc=src.creation_date_utc,
    )


def map_formula_to_expression_dto(src: Formula, mapper: Mapper) -> FormulaExpressionDto:
    return FormulaExpressionDto(
        id=src.id,
        project_definition_id=src.project_definition_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
        path=src.path,
        creation_date_utc=src.creation_date_utc,
    )


def map_aggregate_collection_from_dto(
    src: AggregateCollectionDto, mapper: Mapper
) -> AggregateCollection:
    return AggregateCollection(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        is_abstract=src.is_abstract,
        attributes_schema=mapper.map_many(
            src.attributes_schema, AggregateAttributeSchema
        ),
    )


def map_aggregate_collection_to_dto(
    src: AggregateCollection, mapper: Mapper
) -> AggregateCollectionDto:
    return AggregateCollectionDto(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        is_abstract=src.is_abstract,
        attributes_schema=mapper.map_many(
            src.attributes_schema.values(), AggregateAttributeSchemaDto
        ),
    )


def map_new_aggregate_collection_from_dto(
    src: NewAggregateCollectionDto, mapper: Mapper
) -> NewAggregateCollection:
    return NewAggregateCollection(
        name=src.name,
        is_abstract=src.is_abstract,
        attributes_schema=mapper.map_many(
            src.attributes_schema, AggregateAttributeSchema
        ),
    )


def map_aggregate_attribute_schema_from_dto(
    src: AggregateAttributeSchemaDto, mapper: Mapper
) -> AggregateAttributeSchema:
    return AggregateAttributeSchema(
        name=src.name,
        details=mapper.map(src.details, field_details_union_dto_mappings.from_origin),
    )


def map_aggregate_attributeschema__to_dto(
    src: AggregateAttributeSchema, mapper: Mapper
) -> AggregateAttributeSchemaDto:
    return AggregateAttributeSchemaDto(
        name=src.name,
        details=mapper.map(src.details, field_details_union_dto_mappings.to_origin),
    )


def map_aggregate_from_dto(src: AggregateDto, mapper: Mapper) -> Aggregate:
    return Aggregate(
        id=src.id,
        project_definition_id=src.project_definition_id,
        collection_id=src.collection_id,
        ordinal=src.ordinal,
        name=src.name,
        is_extendable=src.is_extendable,
        attributes={
            attribute.name: mapper.map(attribute, AggregateAttribute)
            for attribute in src.attribute
        },
    )


def map_aggregate_to_dto(src: Aggregate, mapper: Mapper) -> AggregateDto:
    return AggregateDto(
        id=src.id,
        project_definition_id=src.project_definition_id,
        collection_id=src.collection_id,
        ordinal=src.ordinal,
        name=src.name,
        is_extendable=src.is_extendable,
        attributes=[
            mapper.map(attribute, AggregateAttributeDto)
            for attribute in src.attributes.values()
        ],
    )


def map_new_aggregate_from_dto(src: NewAggregateDto, mapper: Mapper) -> NewAggregate:
    return NewAggregate(
        ordinal=src.ordinal,
        name=src.name,
        is_extendable=src.is_extendable,
        attributes=mapper.map_many(src.attributes, AggregateAttribute),
        translated=mapper.map_many(src.translated, FieldTranslation),
    )


def map_aggregate_attribute_to_dto(
    src: AggregateAttribute, mapper: Mapper
) -> AggregateAttributeDto:
    return AggregateAttributeDto(
        name=src.name,
        is_readonly=src.is_readonly,
        value=mapper.map(
            src.value, primitive_with_reference_union_dto_mappings.to_origin
        ),
    )


def map_aggregate_attribute_from_dto(
    src: AggregateAttributeDto, mapper: Mapper
) -> AggregateAttribute:
    return AggregateAttribute(
        name=src.name,
        is_readonly=src.is_readonly,
        value=mapper.map(
            src.value, primitive_with_reference_union_dto_mappings.from_origin
        ),
    )


def map_new_datasheet_from_dto(src: NewDatasheetDto, mapper: Mapper) -> NewDatasheet:
    return NewDatasheet(
        name=src.name,
        project_definition_id=src.project_definition_id,
        abstract_collection_id=src.abstract_collection_id,
    )


def map_datasheet_import_from_dto(src: DatasheetImportDto, mapper: Mapper) -> Datasheet:
    return Datasheet(
        id=src.id,
        name=src.name,
        project_definition_id=src.project_definition_id,
        from_datasheet_id=src.id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_datasheet_to_dto(src: Datasheet, mapper: Mapper) -> DatasheetDto:
    return DatasheetDto(
        id=src.id,
        name=src.name,
        project_definition_id=src.project_definition_id,
        abstract_collection_id=src.abstract_collection_id,
        from_datasheet_id=src.from_datasheet_id,
        attributes_schema=[
            mapper.map(attribute_schema, AggregateAttributeSchemaDto)
            for attribute_schema in src.attributes_schema.values()
        ],
        instances_schema=[
            InstanceSchemaDto(
                id=id,
                is_extendable=instance_schema.is_extendable,
                attributes_schema=[
                    mapper.map(attribute_schema, AggregateAttributeDto)
                    for name, attribute_schema in instance_schema.attributes_schema.items()
                ],
            )
            for id, instance_schema in src.instances_schema.items()
        ],
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_import_from_dto(
    src: DatasheetElementImportDto, mapper: Mapper
) -> DatasheetElement:
    return DatasheetElement(
        id=src.id,
        datasheet_id=src.datasheet_id,
        aggregate_id=src.aggregate_id,
        attributes=[mapper.map(attribute, Attribute) for attribute in src.attributes],
        ordinal=0,
        original_datasheet_id=src.original_datasheet_id,
        original_owner_organization_id=src.original_owner_organization_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_to_dto(
    src: DatasheetElement, mapper: Mapper
) -> DatasheetElementDto:
    return DatasheetElementDto(
        id=src.id,
        datasheet_id=src.datasheet_id,
        aggregate_id=src.aggregate_id,
        ordinal=src.ordinal,
        attributes=[
            mapper.map(attribute, AttributeDto) for attribute in src.attributes
        ],
        original_datasheet_id=src.original_datasheet_id,
        original_owner_organization_id=src.original_owner_organization_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_element_from_dto(
    src: DatasheetElementDto, mapper: Mapper
) -> DatasheetElement:
    return DatasheetElement(
        datasheet_id=src.datasheet_id,
        aggregate_id=src.aggregate_id,
        child_element_reference=src.child_element_reference,
        original_owner_organization_id=src.original_owner_organization_id,
        properties=mapper.map_dict_values(
            src.properties, primitive_union_dto_mappings.from_origin
        ),
        original_datasheet_id=src.original_datasheet_id,
        creation_date_utc=src.creation_date_utc,
    )


def map_attribute_to_dto(src: Attribute, mapper: Mapper) -> AttributeDto:
    return AttributeDto(
        name=src.name,
        value=mapper.map(
            src.value, primitive_with_reference_union_dto_mappings.to_origin
        ),
    )


def map_attribute_from_dto(src: AttributeDto, mapper: Mapper) -> Attribute:
    return Attribute(
        name=src.name,
        value=mapper.map(
            src.value, primitive_with_reference_union_dto_mappings.from_origin
        ),
    )


def map_datasheet_clone_target_from_dto(
    src: CloningDatasheetDto, mapper: Mapper
) -> CloningDatasheet:
    return CloningDatasheet(
        target_datasheet_id=src.target_datasheet_id, clone_name=src.clone_name
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
        stage_summary=mapper.map(src.stage_summary, ReportComputation),
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
        stage_summary=mapper.map(src.stage_summary, ReportComputationDto),
        report_summary=mapper.map_many(src.report_summary, ReportComputationDto),
        joins_cache=mapper.map_many(src.joins_cache, ReportJoinDto),
        columns=mapper.map_many(src.columns, ReportComputationDto),
        group_by=mapper.map_many(src.group_by, AttributeBucketDto),
        order_by=mapper.map_many(src.order_by, AttributeBucketDto),
    )


def map_stage_grouping_to_dto(
    src: ReportComputation, mapper: Mapper
) -> ReportComputationDto:
    return ReportComputationDto(
        label=mapper.map(src.label, AttributeBucketDto),
        summary=mapper.map(src.summary, ReportComputationDto),
    )


def map_stage_grouping_from_dto(
    src: ReportComputationDto, mapper: Mapper
) -> ReportComputation:
    return ReportComputation(
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
        aggregate_id=src.aggregate_id,
        element_id=src.element_id,
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
        aggregate_id=src.aggregate_id,
        element_id=src.element_id,
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
        aggregate_id=src.aggregate_id,
        element_id=src.element_id,
        organization_id=src.organization_id,
    )


def map_measure_unit_to_dto(src: MeasureUnit, mapper: Mapper) -> MeasureUnitDto:
    return MeasureUnitDto(id=src.id)


def map_formula_to_core_definition_node_dto(
    src: Formula, mapper: Mapper
) -> CoreDefinitionNodeDto:
    return CoreDefinitionNodeDto(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        path=src.path,
    )


def map_definition_node_to_core_definition_node_dto(
    src: ProjectDefinitionNode, mapper: Mapper
) -> CoreDefinitionNodeDto:
    return CoreDefinitionNodeDto(
        id=src.id,
        project_definition_id=src.project_definition_id,
        name=src.name,
        path=src.path,
    )


def map_new_definition_dto(src: NewDefinitionDto, mapper: Mapper) -> ProjectDefinition:
    return ProjectDefinition(
        id=mapper.get(IdProvider).uuid4(),
        creation_date_utc=mapper.get(Clock).utcnow(),
        name=src.name,
    )


def map_new_datasheet_element_from_dto(
    src: NewDatasheetElementDto, mapper: Mapper
) -> NewDatasheetElement:
    return NewDatasheetElement(
        aggregate_id=src.aggregate_id,
        ordinal=src.ordinal,
        attributes=mapper.map_many(src.attributes, Attribute),
    )

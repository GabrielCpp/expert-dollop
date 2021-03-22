import astor
from dataclasses import asdict
from expert_dollup.shared.starlette_injection import Clock
from expert_dollup.shared.automapping import Mapper
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
        config=src.config,
        value_type=src.value_type,
        default_value=src.default_value,
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
        config=src.config,
        value_type=src.value_type,
        default_value=src.default_value,
        path=src.path,
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


def map_project_from_dto(src: ProjectDto, mapper: Mapper) -> Project:
    return Project(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_project_to_dto(src: Project, mapper: Mapper) -> ProjectDto:
    return ProjectDto(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_project_container_from_dto(
    src: ProjectContainerDto, mapper: Mapper
) -> ProjectContainer:
    return ProjectContainer(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        path=src.path,
        value=src.value,
    )


def map_project_container_to_dto(
    src: ProjectContainer, mapper: Mapper
) -> ProjectContainerDto:
    return ProjectContainerDto(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        path=src.path,
        value=src.value,
    )


def map_project_container_page_to_dto(
    src: Page, mapper: Mapper
) -> ProjectContainerPageDto:
    return ProjectContainerPageDto(
        next_page_token=src.next_page_token,
        limit=src.limit,
        results=mapper.map_many(src.results, ProjectContainerDto),
    )


def map_project_container_meta_to_dto(
    src: ProjectContainerMeta, mapper: Mapper
) -> ProjectContainerMetaDto:
    return ProjectContainerMetaDto(
        project_id=src.project_id,
        type_id=src.type_id,
        state=ProjectContainerMetaStateDto(**asdict(src.state)),
    )


def map_project_container_node_to_dto(
    src: ProjectContainerNode, mapper: Mapper
) -> ProjectContainerNodeDto:
    return ProjectContainerNodeDto(
        container=mapper.map(src.container, ProjectContainerDto),
        definition=mapper.map(src.definition, ProjectDefinitionNodeDto),
        meta=mapper.map(src.meta, ProjectContainerMetaDto),
        children=mapper.map_many(src.children, ProjectContainerNodeDto),
    )


def map_projec_container_tree_to_dto(
    src: ProjectContainerTree, mapper: Mapper
) -> ProjectContainerTreeDto:
    return ProjectContainerTreeDto(
        roots=mapper.map_many(src.roots, ProjectContainerNodeDto)
    )


def map_translation_from_dto(src: TranslationDto, mapper: Mapper) -> Translation:
    return Translation(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        scope=src.scope,
        value=src.value,
        creation_date_utc=mapper.get(Clock).utcnow(),
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


def map_page_translation_to_dto(
    src: Page[Translation], mapper: Mapper
) -> TranslationPageDto:
    return Page(
        next_page_token=src.next_page_token,
        limit=src.limit,
        results=mapper.map_many(src.results, TranslationDto, Translation),
    )


def map_formula_from_dto(src: FormulaDto, mapper: Mapper) -> Formula:
    return Formula(
        id=src.id,
        project_def_id=src.project_def_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
        generated_ast=None,
    )


def map_formula_to_dto(src: Formula, mapper: Mapper) -> FormulaDto:
    return FormulaDto(
        id=src.id,
        project_def_id=src.project_def_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
        generated_ast=astor.to_source(src.generated_ast),
    )


def map_datasheet_definition_to_dto(
    src: DatasheetDefinition, mapper: Mapper
) -> DatasheetDefinitionDto:
    return DatasheetDefinitionDto(
        id=src.id,
        name=src.name,
        element_properties_schema=src.element_properties_schema,
    )


def map_datasheet_definition_from_dto(
    src: DatasheetDefinitionDto, mapper: Mapper
) -> DatasheetDefinition:
    return DatasheetDefinition(
        id=src.id,
        name=src.name,
        element_properties_schema=src.element_properties_schema,
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


def map_label_collection_from_dto(
    src: LabelCollectionDto, mapper: Mapper
) -> LabelCollection:
    return LabelCollection(
        id=src.id,
        datasheet_definition_id=src.datasheet_definition_id,
        name=src.name,
    )


def map_label_collection_to_dto(
    src: LabelCollection, mapper: Mapper
) -> LabelCollectionDto:
    return LabelCollectionDto(
        id=src.id,
        datasheet_definition_id=src.datasheet_definition_id,
        name=src.name,
    )


def map_datasheet_definition_label_to_dto(src: Label, mapper: Mapper) -> LabelDto:
    return LabelDto(
        id=src.id,
        label_collection_id=src.label_collection_id,
        order_index=src.order_index,
    )


def map_datasheet_definition_label_from_dto(src: LabelDto, mapper: Mapper) -> Label:
    return Label(
        id=src.id,
        label_collection_id=src.label_collection_id,
        order_index=src.order_index,
    )


def map_new_datasheet_from_dto(src: NewDatasheetDto, mapper: Mapper) -> Datasheet:
    return Datasheet(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        datasheet_def_id=src.datasheet_def_id,
        from_datasheet_id=src.from_datasheet_id,
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

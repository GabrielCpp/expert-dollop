import jsonpickle
from typing import List
from expert_dollup.shared.starlette_injection import Clock
from uuid import UUID
from dataclasses import asdict
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import map_dict_keys
from expert_dollup.core.utils.path_transform import (
    join_path,
    split_uuid_path,
    join_uuid_path,
    build_path_steps,
    list_uuid_to_str,
    list_str_to_uuid,
)

from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.core.domains import *


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
        config=jsonpickle.decode(src.config),
        default_value=None
        if src.default_value is None
        else jsonpickle.decode(src.default_value),
        path=split_uuid_path(src.path),
        creation_date_utc=src.creation_date_utc,
    )


def map_project_definition_node_to_dao(
    src: ProjectDefinitionNode, mapper: Mapper
) -> ProjectDefinitionNodeDao:
    display_query_internal_id = src.project_def_id
    level = len(src.path)

    if level >= SECTION_LEVEL and level <= FORM_LEVEL:
        display_query_internal_id = src.path[ROOT_LEVEL]
    elif level > FORM_LEVEL:
        display_query_internal_id = src.path[FORM_LEVEL]

    return ProjectDefinitionNodeDao(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        config=jsonpickle.encode(src.config),
        path=join_uuid_path(src.path),
        display_query_internal_id=display_query_internal_id,
        level=len(src.path),
        creation_date_utc=mapper.get(Clock).utcnow(),
        default_value=None
        if src.default_value is None
        else jsonpickle.encode(src.default_value),
    )


def map_project_from_dao(src: ProjectDao, mapper: Mapper) -> Project:
    return Project(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_project_to_dao(src: Project, mapper: Mapper) -> ProjectDao:
    return ProjectDao(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_project_container_to_dao(
    src: ProjectContainer, mapper: Mapper
) -> ProjectContainerDao:
    return ProjectContainerDao(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        path=join_uuid_path(src.path),
        value=None if src.value is None else jsonpickle.encode(src.value),
        mixed_paths=build_path_steps(src.path),
        creation_date_utc=mapper.get(Clock).utcnow(),
    )


def map_project_container_from_dao(
    src: ProjectContainerDao, mapper: Mapper
) -> ProjectContainer:
    return ProjectContainer(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        path=split_uuid_path(src.path),
        value=None if src.value is None else jsonpickle.decode(src.value),
    )


def map_project_container_meta_to_dao(
    src: ProjectContainerMeta, mapper: Mapper
) -> ProjectContainerMetaDao:
    return ProjectContainerMetaDao(
        project_id=src.project_id,
        type_id=src.type_id,
        state=asdict(src.state),
    )


def map_project_container_meta_from_dao(
    src: ProjectContainerMetaDao, mapper: Mapper
) -> ProjectContainerMeta:
    return ProjectContainerMeta(
        project_id=src.project_id,
        type_id=src.type_id,
        state=ProjectContainerMetaState(**src.state),
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
            "config": ("config", jsonpickle.encode),
            "default_value": ("default_value", jsonpickle.encode),
            "path": ("default_value", join_uuid_path),
        },
    )


def map_project_container_filter_to_dict(
    src: ProjectContainerFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "id": ("id", None),
            "project_id": ("project_id", None),
            "type_id": ("type_id", None),
            "path": ("path", None),
            "value": ("value", jsonpickle.encode),
        },
    )


def map_project_container_meta_filter_to_dict(
    src: ProjectContainerMetaFilter, mapper: Mapper
) -> dict:
    return map_dict_keys(
        src.args,
        {
            "project_id": ("project_id", None),
            "type_id": ("type_id", None),
        },
    )


def map_formula_to_dao(src: Formula, mapper: Mapper) -> ProjectDefinitionFormulaDao:
    return ProjectDefinitionFormulaDao(
        id=src.id,
        project_def_id=src.project_def_id,
        attached_to_type_id=src.attached_to_type_id,
        name=src.name,
        expression=src.expression,
        generated_ast=jsonpickle.encode(src.generated_ast),
    )


def map_formula_cache_result_to_dao(
    src: FormulaCachedResult, mapper: Mapper
) -> ProjectFormulaCacheDao:
    return ProjectFormulaCacheDao(
        project_id=src.project_id,
        formula_id=src.formula_id,
        container_id=src.container_id,
        generation_tag=src.generation_tag,
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
        container_id=src.container_id,
        generation_tag=src.generation_tag,
        calculation_details=src.calculation_details,
        result=src.result,
    )


def map_datasheet_definition_to_dao(
    src: DatasheetDefinition, mapper: Mapper
) -> DatasheetDefinitionDao:
    return DatasheetDefinitionDao(
        id=src.id,
        name=src.name,
        element_properties_schema=src.element_properties_schema,
    )


def map_datasheet_definition_from_dao(
    src: DatasheetDefinitionDao, mapper: Mapper
) -> DatasheetDefinition:
    return DatasheetDefinition(
        id=src.id,
        name=src.name,
        element_properties_schema=src.element_properties_schema,
    )


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
            name: asdict(property_details)
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
            name: DatasheetDefinitionElementProperty(**item_property)
            for name, item_property in src.default_properties.items()
        },
        tags=list_str_to_uuid(src.tags),
        creation_date_utc=src.creation_date_utc,
    )


def map_datasheet_definition_label_collection_from_dao(
    src: LabelCollectionDao, mapper: Mapper
) -> LabelCollection:
    return LabelCollection(
        id=src.id,
        datasheet_definition_id=src.datasheet_definition_id,
        name=src.name,
    )


def map_datasheet_definition_label_collection_to_dao(
    src: LabelCollection, mapper: Mapper
) -> LabelCollectionDao:
    return LabelCollectionDao(
        id=src.id,
        datasheet_definition_id=src.datasheet_definition_id,
        name=src.name,
    )


def map_datasheet_definition_label_to_dao(src: Label, mapper: Mapper) -> LabelDao:
    return LabelDao(
        id=src.id,
        label_collection_id=src.label_collection_id,
        order_index=src.order_index,
    )


def map_datasheet_definition_label_from_dao(src: LabelDao, mapper: Mapper) -> Label:
    return Label(
        id=src.id,
        label_collection_id=src.label_collection_id,
        order_index=src.order_index,
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
    return asdict(src)


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
    return asdict(src)

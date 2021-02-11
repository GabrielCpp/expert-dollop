from typing import List
from datetime import datetime
from uuid import UUID
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import map_dict_keys
from expert_dollup.infra.path_transform import (
    join_path,
    split_uuid_path,
    join_uuid_path,
    build_path_steps,
)

from expert_dollup.infra.expert_dollup_db import *
from expert_dollup.core.domains import *


def map_project_definition_value_type_from_dao(
    src: ProjectDefinitionValueTypeDao, mapper: Mapper
) -> ProjectDefinitionValueType:
    return ProjectDefinitionValueType(
        id=src.id,
        value_json_schema=src.value_json_schema,
        attributes_json_schema=src.attributes_json_schema,
        display_name=src.display_name,
    )


def map_project_definition_from_dao(
    src: ProjectDefinitionDao, mapper: Mapper
) -> ProjectDefinition:
    return ProjectDefinition(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
    )


def map_project_definition_to_dao(
    src: ProjectDefinition, mapper: Mapper
) -> ProjectDefinitionDao:
    return ProjectDefinitionDao(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        creation_date_utc=datetime.utcnow(),
    )


def map_project_definition_container_from_dao(
    src: ProjectDefinitionContainerDao, mapper: Mapper
) -> ProjectDefinitionContainer:
    return ProjectDefinitionContainer(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        config=src.config,
        value_type=src.value_type,
        default_value=src.default_value,
        path=split_uuid_path(src.path),
    )


def map_project_definition_container_to_dao(
    src: ProjectDefinitionContainer, mapper: Mapper
) -> ProjectDefinitionContainerDao:
    return ProjectDefinitionContainerDao(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        config=src.config,
        value_type=src.value_type,
        default_value=src.default_value,
        path=join_uuid_path(src.path),
        mixed_paths=build_path_steps(src.path),
        creation_date_utc=datetime.utcnow(),
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
        creation_date_utc=datetime.utcnow(),
    )


def map_project_container_to_dao(
    src: ProjectContainer, mapper: Mapper
) -> ProjectContainerDao:
    return ProjectContainerDao(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        path=join_uuid_path(src.path),
        value=src.value,
        mixed_paths=build_path_steps(src.path),
        creation_date_utc=datetime.utcnow(),
    )


def map_project_container_from_dao(
    src: ProjectContainerDao, mapper: Mapper
) -> ProjectContainer:
    return ProjectContainer(
        id=src.id,
        project_id=src.project_id,
        type_id=src.type_id,
        path=split_uuid_path(src.path),
        value=src.value,
    )


def map_project_container_meta_to_dao(
    src: ProjectContainerMeta, mapper: Mapper
) -> ProjectContainerMetaDao:
    return ProjectContainerMetaDao(
        project_id=src.project_id,
        type_id=src.type_id,
        state=src.state,
    )


def map_project_container_meta_from_dao(
    src: ProjectContainerMetaDao, mapper: Mapper
) -> ProjectContainerMeta:
    return ProjectContainerMeta(
        project_id=src.project_id,
        type_id=src.type_id,
        state=src.state,
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
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        value=src.value,
    )


def map_translation_to_dao(src: Translation, mapper: Mapper) -> TranslationDao:
    return TranslationDao(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        value=src.value,
    )


def map_translation_id_to_dict(src: TranslationId, mapper: Mapper) -> dict:
    return dict(ressource_id=src.ressource_id, locale=src.locale, name=src.name)


def map_project_definition_container_filter_to_dict(
    src: ProjectDefinitionContainerFilter, mapper: Mapper
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
            "config": ("config", None),
            "value_type": ("value_type", None),
            "default_value": ("default_value", None),
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
            "value": ("value", None),
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
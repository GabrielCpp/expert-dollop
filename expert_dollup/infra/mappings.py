from typing import List
from datetime import datetime
from uuid import UUID
from expert_dollup.shared.automapping import Mapper
from expert_dollup.infra.path_transform import (
    join_path,
    split_uuid_path,
    join_uuid_path,
)
from expert_dollup.infra.expert_dollup_db import (
    ProjectDefinitionDao,
    ProjectDefinitionContainerDao,
    ProjectDao,
    RessourceDao,
    TranslationDao,
    ProjectDefinitionValueTypeDao,
)
from expert_dollup.core.domains import (
    ProjectDefinition,
    ProjectDefinitionContainer,
    Project,
    Ressource,
    Translation,
    TranslationId,
    ProjectDefinitionValueType,
)


def map_project_definition_value_type_from_dao(
    src: ProjectDefinitionValueTypeDao, mapper: Mapper = None
) -> ProjectDefinitionValueType:
    return ProjectDefinitionValueType(
        id=src.id,
        value_json_schema=src.value_json_schema,
        attributes_json_schema=src.attributes_json_schema,
        display_name=src.display_name,
    )


def map_project_definition_from_dao(
    src: ProjectDefinitionDao, mapper: Mapper = None
) -> ProjectDefinition:
    return ProjectDefinition(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
    )


def map_project_definition_to_dao(
    src: ProjectDefinition, mapper: Mapper = None
) -> ProjectDefinitionDao:
    return ProjectDefinitionDao(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        creation_date_utc=datetime.utcnow(),
    )


def map_project_definition_container_from_dao(
    src: ProjectDefinitionContainerDao, mapper: Mapper = None
) -> ProjectDefinitionContainer:
    return ProjectDefinitionContainer(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        custom_attributes=src.custom_attributes,
        value_type=src.value_type,
        default_value=src.default_value,
        path=split_uuid_path(src.path),
    )


def map_project_definition_container_to_dao(
    src: ProjectDefinitionContainer, mapper: Mapper = None
) -> ProjectDefinitionContainerDao:
    def mix_path(path: List[str]) -> List[str]:
        mixed_path: List[str] = []

        for upper_index in range(2, len(path)):
            mixed_path.append(join_path(path[0:upper_index]))

        return mixed_path

    str_path = [str(item) for item in src.path]

    return ProjectDefinitionContainerDao(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        custom_attributes=src.custom_attributes,
        value_type=src.value_type,
        default_value=src.default_value,
        path=join_uuid_path(src.path),
        mixed_paths=mix_path(str_path),
        creation_date_utc=datetime.utcnow(),
    )


def map_project_from_dao(src: ProjectDao, mapper: Mapper = None) -> Project:
    return Project(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_project_to_dao(src: Project, mapper: Mapper = None) -> ProjectDao:
    return ProjectDao(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_ressource_from_dao(src: RessourceDao, mapper: Mapper = None) -> Ressource:
    return Ressource(
        id=src.id,
        name=src.name,
        owner_id=src.owner_id,
    )


def map_ressource_to_dao(src: Ressource, mapper: Mapper = None) -> RessourceDao:
    return RessourceDao(
        id=src.id,
        name=src.name,
        owner_id=src.owner_id,
    )


def map_translation_from_dao(src: TranslationDao, mapper: Mapper = None) -> Translation:
    return Translation(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        value=src.value,
    )


def map_translation_to_dao(src: Translation, mapper: Mapper = None) -> TranslationDao:
    return TranslationDao(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        value=src.value,
    )


def map_translation_id_to_dict(src: TranslationId, mapper: Mapper = None) -> dict:
    return dict(ressource_id=src.ressource_id, locale=src.locale, name=src.name)

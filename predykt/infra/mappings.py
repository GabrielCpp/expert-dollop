from typing import List
from datetime import datetime
from uuid import UUID
from predykt.shared.automapping import Mapper
from predykt.infra.path_transform import join_path, split_uuid_path, join_uuid_path
from predykt.infra.predykt_db import (
    ProjectDefinitionDao,
    ProjectDefinitionContainerDao,
    ProjectDefinitionPackageDao,
    ProjectDefinitionStructDao,
    ProjectDefinitionFunctionDao,
    ProjectDao,
    RessourceDao,
    TranslationDao,
)
from predykt.core.domains import (
    ProjectDefinition,
    ProjectDefinitionContainer,
    ProjectDefinitionPackage,
    ProjectDefinitionStruct,
    ProjectDefinitionFunction,
    Project,
    Ressource,
    Translation,
    TranslationId,
)


def map_project_definition_from_dao(
    src: ProjectDefinitionDao, mapper: Mapper = None
) -> ProjectDefinition:
    return ProjectDefinition(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        plugins=src.plugins
    )


def map_project_definition_to_dao(
    src: ProjectDefinition, mapper: Mapper = None
) -> ProjectDefinitionDao:
    return ProjectDefinitionDao(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        plugins=src.plugins,
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
        custom_attributes=src.custom_attributes,
        value_type=src.value_type,
        default_value=src.default_value,
        path=join_uuid_path(src.path),
        mixed_paths=mix_path(str_path),
        creation_date_utc=datetime.utcnow(),
    )


def map_project_definition_package_from_dao(
    src: ProjectDefinitionPackageDao, mapper: Mapper = None
) -> ProjectDefinitionPackage:
    return ProjectDefinitionPackage(
        id=src.id, project_def_id=src.project_def_id, name=src.name, package=src.package
    )


def map_project_definition_package_to_dao(
    src: ProjectDefinitionPackage, mapper: Mapper = None
) -> ProjectDefinitionPackageDao:
    return ProjectDefinitionPackageDao(
        id=src.id, project_def_id=src.project_def_id, name=src.name, package=src.package
    )


def map_project_definition_struct_from_dao(
    src: ProjectDefinitionStructDao, mapper: Mapper = None
) -> ProjectDefinitionStruct:
    return ProjectDefinitionStruct(
        id=src.id,
        name=src.name,
        package_id=src.package_id,
        properties=src.properties,
        dependencies=src.dependencies,
    )


def map_project_definition_struct_to_dao(
    src: ProjectDefinitionStruct, mapper: Mapper = None
) -> ProjectDefinitionStructDao:
    return ProjectDefinitionStructDao(
        id=src.id,
        name=src.name,
        package_id=src.package_id,
        properties=src.properties,
        dependencies=src.dependencies,
    )


def map_project_definition_function_from_dao(
    src: ProjectDefinitionFunctionDao, mapper: Mapper = None
) -> ProjectDefinitionFunction:
    return ProjectDefinitionFunction(
        id=src.id,
        name=src.name,
        code=src.code,
        ast=src.ast,
        signature=src.signature,
        dependencies=src.dependencies,
        struct_id=src.struct_id,
        package_id=src.package_id,
    )


def map_project_definition_function_to_dao(
    src: ProjectDefinitionFunction, mapper: Mapper = None
) -> ProjectDefinitionFunctionDao:
    return ProjectDefinitionFunctionDao(
        id=src.id,
        name=src.name,
        code=src.code,
        ast=src.ast,
        signature=src.signature,
        dependencies=src.dependencies,
        struct_id=src.struct_id,
        package_id=src.package_id,
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
    return dict(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name
    )

from predykt.shared.automapping import Mapper
from predykt.app.dtos import (
    ProjectDefinitionDto,
    ProjectDefinitionContainerDto,
    ProjectDefinitionPackageDto,
    ProjectDefinitionStructDto,
    ProjectDefinitionFunctionDto,
    ProjectDto,
    TranslationDto,
    TranslationIdDto,
)
from predykt.core.domains import (
    ProjectDefinition,
    ProjectDefinitionContainer,
    ProjectDefinitionPackage,
    ProjectDefinitionStruct,
    ProjectDefinitionFunction,
    Project,
    Translation,
    TranslationId,
)


def map_project_definition_from_dto(
    src: ProjectDefinitionDto, mapper: Mapper = None
) -> ProjectDefinition:
    return ProjectDefinition(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        plugins=src.plugins
    )


def map_project_definition_to_dto(
    src: ProjectDefinition, mapper: Mapper = None
) -> ProjectDefinitionDto:
    return ProjectDefinitionDto(
        id=src.id,
        name=src.name,
        default_datasheet_id=src.default_datasheet_id,
        plugins=src.plugins
    )


def map_project_definition_container_from_dto(
    src: ProjectDefinitionContainerDto, mapper: Mapper = None
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
        path=src.path,
    )


def map_project_definition_container_to_dto(
    src: ProjectDefinitionContainer, mapper: Mapper = None
) -> ProjectDefinitionContainerDto:
    return ProjectDefinitionContainerDto(
        id=src.id,
        project_def_id=src.project_def_id,
        name=src.name,
        is_collection=src.is_collection,
        instanciate_by_default=src.instanciate_by_default,
        order_index=src.order_index,
        custom_attributes=src.custom_attributes,
        value_type=src.value_type,
        default_value=src.default_value,
        path=src.path,
    )


def map_project_definition_package_from_dto(
    src: ProjectDefinitionPackageDto, mapper: Mapper = None
) -> ProjectDefinitionPackage:
    return ProjectDefinitionPackage(
        id=src.id, project_def_id=src.project_def_id, name=src.name, package=src.package
    )


def map_project_definition_package_to_dto(
    src: ProjectDefinitionPackage, mapper: Mapper = None
) -> ProjectDefinitionPackageDto:
    return ProjectDefinitionPackageDto(
        id=src.id, project_def_id=src.project_def_id, name=src.name, package=src.package
    )


def map_project_definition_struct_from_dto(
    src: ProjectDefinitionStructDto, mapper: Mapper = None
) -> ProjectDefinitionStruct:
    return ProjectDefinitionStruct(
        id=src.id,
        name=src.name,
        package_id=src.package_id,
        properties=src.properties,
        dependencies=src.dependencies,
    )


def map_project_definition_struct_to_dto(
    src: ProjectDefinitionStruct, mapper: Mapper = None
) -> ProjectDefinitionStructDto:
    return ProjectDefinitionStructDto(
        id=src.id,
        name=src.name,
        package_id=src.package_id,
        properties=src.properties,
        dependencies=src.dependencies,
    )


def map_project_definition_function_from_dto(
    src: ProjectDefinitionFunctionDto, mapper: Mapper = None
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


def map_project_definition_function_to_dto(
    src: ProjectDefinitionFunction, mapper: Mapper = None
) -> ProjectDefinitionFunctionDto:
    return ProjectDefinitionFunctionDto(
        id=src.id,
        name=src.name,
        code=src.code,
        ast=src.ast,
        signature=src.signature,
        dependencies=src.dependencies,
        struct_id=src.struct_id,
        package_id=src.package_id,
    )


def map_project_from_dto(src: ProjectDto, mapper: Mapper = None) -> Project:
    return Project(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_project_to_dto(src: Project, mapper: Mapper = None) -> ProjectDto:
    return ProjectDto(
        id=src.id,
        name=src.name,
        is_staged=src.is_staged,
        project_def_id=src.project_def_id,
        datasheet_id=src.datasheet_id,
    )


def map_translation_from_dto(src: TranslationDto, mapper: Mapper = None) -> Translation:
    return Translation(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        value=src.value,
    )


def map_translation_to_dto(src: Translation, mapper: Mapper = None) -> TranslationDto:
    return TranslationDto(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
        value=src.value,
    )


def map_translation_id_from_dto(src: TranslationIdDto, mapper: Mapper = None) -> TranslationId:
    return TranslationId(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
    )


def map_translation_id_to_dto(src: TranslationId, mapper: Mapper = None) -> TranslationIdDto:
    return TranslationDto(
        ressource_id=src.ressource_id,
        locale=src.locale,
        name=src.name,
    )

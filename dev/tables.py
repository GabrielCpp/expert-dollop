from typing import List
from pydantic import BaseModel
from expert_dollup.shared.automapping import Mapper
from expert_dollup.infra.expert_dollup_db import (
    ProjectDefinitionDao,
    TranslationDao,
    ProjectDefinitionContainerDao,
    project_definition_table,
    project_definition_container_table,
    translation_table,
)

from expert_dollup.core.domains import (
    ProjectDefinition,
    ProjectDefinitionContainer,
    Translation,
)


from expert_dollup.app.dtos import (
    ProjectDefinitionDto,
    ProjectDefinitionContainerDto,
    TranslationDto,
)


class Tables(BaseModel):
    project_definitions: List[ProjectDefinitionDao]
    project_definition_containers: List[ProjectDefinitionContainerDao]
    translations: List[TranslationDao]


class TablesDto(BaseModel):
    project_definitions: List[ProjectDefinitionDto]
    project_definition_containers: List[ProjectDefinitionContainerDto]
    translations: List[TranslationDto]


def to_dto(tables: Tables, mapper: Mapper) -> TablesDto:
    def double_map(data, current_type, domain_type, dto_type):
        return mapper.map_many(
            mapper.map_many(data, domain_type, current_type), dto_type
        )

    return TablesDto(
        project_definitions=double_map(
            tables.project_definitions,
            ProjectDefinitionDao,
            ProjectDefinition,
            ProjectDefinitionDto,
        ),
        project_definition_containers=double_map(
            tables.project_definition_containers,
            ProjectDefinitionContainerDao,
            ProjectDefinitionContainer,
            ProjectDefinitionContainerDto,
        ),
        translations=double_map(
            tables.translations, TranslationDao, Translation, TranslationDto
        ),
    )


def insert(tables: Tables, database) -> None:
    database.execute(
        project_definition_table.insert(),
        [element.dict() for element in tables.project_definitions],
    )

    database.execute(
        project_definition_container_table.insert(),
        [element.dict() for element in tables.project_definition_containers],
    )

    database.execute(
        translation_table.insert(), [element.dict() for element in tables.translations]
    )

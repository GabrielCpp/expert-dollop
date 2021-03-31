import os
from dotenv import load_dotenv
from enum import Enum
from typing import List, Dict, Any
from dataclasses import dataclass, field
from os.path import join
from injector import inject
from sqlalchemy import MetaData, create_engine
from expert_dollup.core.domains import *
from expert_dollup.infra.services import *


@dataclass
class FakeExpertDollupDb:
    project_definition_nodes: List[ProjectDefinitionNode] = field(default_factory=list)
    project_definitions: List[ProjectDefinition] = field(default_factory=list)
    datasheet_definitions: List[DatasheetDefinition] = field(default_factory=list)
    datasheet_definition_elements: List[DatasheetDefinitionElement] = field(
        default_factory=list
    )
    label_collections: List[LabelCollection] = field(default_factory=list)
    labels: List[Label] = field(default_factory=list)
    translations: List[Translation] = field(default_factory=list)


def truncate_db():
    load_dotenv()
    DATABASE_URL = "postgresql://{}:{}@{}/{}".format(
        os.environ["POSTGRES_USERNAME"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_DB"],
    )

    engine = create_engine(DATABASE_URL)
    meta = MetaData()
    meta.reflect(bind=engine)
    con = engine.connect()
    trans = con.begin()
    for table in meta.sorted_tables:
        if table.name in ["project_definition_value_type"]:
            continue

        con.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
        con.execute(table.delete())
        con.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
    trans.commit()


async def populate_db(db, table, daos: Dict[str, Any]):
    await db.execute_many(table.insert(), [dao.dict() for dao in daos.values()])


@inject
class DbSetupHelper:
    def __init__(
        self,
        project_definition_node_service: ProjectDefinitionNodeService,
        project_definition_service: ProjectDefinitionService,
        translation_service: TranslationService,
        datasheet_definition_service: DatasheetDefinitionService,
        datasheet_definition_element_service: DatasheetDefinitionElementService,
        label_collection_service: LabelCollectionService,
        label_service: LabelService,
    ):
        self.project_definition_node_service = project_definition_node_service
        self.project_definition_service = project_definition_service
        self.translation_service = translation_service
        self.datasheet_definition_service = datasheet_definition_service
        self.datasheet_definition_element_service = datasheet_definition_element_service
        self.label_collection_service = label_collection_service
        self.label_service = label_service

    async def init_db(self, fake_db: FakeExpertDollupDb):
        await self.project_definition_service.insert_many(fake_db.project_definitions)

        await self.project_definition_node_service.insert_many(
            fake_db.project_definition_nodes,
        )

        await self.translation_service.insert_many(fake_db.translations)
        await self.datasheet_definition_service.insert_many(
            fake_db.datasheet_definitions
        )
        await self.datasheet_definition_element_service.insert_many(
            fake_db.datasheet_definition_elements
        )
        await self.label_collection_service.insert_many(fake_db.label_collections)
        await self.label_service.insert_many(fake_db.labels)

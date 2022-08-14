from pymongo import DESCENDING, ASCENDING
from os import environ

version = "1"


async def create_global_table(db):
    await db.create_collection("settings")
    translation = await db.create_collection("translation")
    await translation.create_index("translation")
    await translation.create_index([("ressource_id", DESCENDING), ("scope", ASCENDING)])


async def create_project_definition_tables(db):
    project_definition = await db.create_collection("project_definition")
    await project_definition.create_index("name")

    project_definition_node = await db.create_collection("project_definition_node")
    await project_definition_node.create_index(
        [("project_definition_id", DESCENDING), ("path", ASCENDING)]
    )
    await project_definition_node.create_index("display_query_internal_id")
    await project_definition_node.create_index(
        [("project_definition_id", DESCENDING), ("name", ASCENDING)]
    )

    project_definition_formula = await db.create_collection(
        "project_definition_formula"
    )
    await project_definition_formula.create_index(
        [("project_definition_id", DESCENDING), ("name", ASCENDING)]
    )


async def create_project_tables(db):
    await db.create_collection("project")
    project_node = await db.create_collection("project_node")
    await project_node.create_index("display_query_internal_id")
    await project_node.create_index([("project_id", DESCENDING), ("path", ASCENDING)])
    await project_node.create_index([("project_id", DESCENDING), ("level", ASCENDING)])

    project_node_metadata = await db.create_collection("project_node_metadata")
    await project_node_metadata.create_index("display_query_internal_id")


async def create_datasheet_tables(db):
    await db.create_collection("unit")
    datasheet_definition_label = await db.create_collection(
        "datasheet_definition_label"
    )
    await datasheet_definition_label.create_index("label_collection_id")

    await db.create_collection("datasheet_definition_element")
    await db.create_collection("datasheet")
    datasheet_element = await db.create_collection("datasheet_element")
    await datasheet_element.create_index("element_def_id")
    await datasheet_element.create_index("original_datasheet_id")


async def create_report_tables(db):
    await db.create_collection("report_definition")
    await db.create_collection("distributable_items")
    await db.create_collection("distribution")


async def upgrade(db):
    await create_global_table(db)
    await create_project_definition_tables(db)
    await create_project_tables(db)
    await create_datasheet_tables(db)
    await create_report_tables(db)

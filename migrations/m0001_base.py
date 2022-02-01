from asyncio import run
from pymongo import DESCENDING, ASCENDING
from os import environ
from urllib.parse import urlsplit, urlunsplit
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
u = urlsplit(environ["DATABASE_URL"])
db_name = u.path.strip(" /")
c = urlunsplit((u.scheme, u.netloc, "admin", u.query, u.fragment))


async def create_global_table(db):
    await db.create_collection("settings")
    await db.create_collection("ressource")
    translation = await db.create_collection("translation")

    await translation.create_index("translation")
    await translation.create_index([("ressource_id", DESCENDING), ("scope", ASCENDING)])


async def create_project_definition_tables(db):
    project_definition = await db.create_collection("project_definition")
    await project_definition.create_index("name")

    project_definition_node = await db.create_collection("project_definition_node")
    await project_definition_node.create_index(
        [("project_def_id", DESCENDING), ("path", ASCENDING)]
    )
    await project_definition_node.create_index("display_query_internal_id")
    await project_definition_node.create_index(
        [("project_def_id", DESCENDING), ("name", ASCENDING)]
    )

    project_definition_formula = await db.create_collection(
        "project_definition_formula"
    )
    await project_definition_formula.create_index(
        [("project_def_id", DESCENDING), ("name", ASCENDING)]
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
    await db.create_collection("datasheet_definition")
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


async def upgrade():
    client = AsyncIOMotorClient(str(c))
    db = client.get_database(db_name)

    await create_global_table(db)
    await create_project_definition_tables(db)
    await create_project_tables(db)
    await create_datasheet_tables(db)
    await create_report_tables(db)

    await db.command(
        "createUser",
        u.username,
        pwd=u.password,
        roles=["readWrite", "dbAdmin", "dbOwner"],
    )


run(upgrade())
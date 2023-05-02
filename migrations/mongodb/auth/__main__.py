from asyncio import run
from os import environ, listdir, path
from urllib.parse import urlsplit, urlunsplit
from motor.motor_asyncio import AsyncIOMotorClient
from importlib import import_module


async def main():
    u = urlsplit(environ["DB_URL"])
    db_name = u.path.strip(" /")
    client = AsyncIOMotorClient(
        str(urlunsplit((u.scheme, u.netloc, "admin", u.query, u.fragment)))
    )
    db = client.get_database(db_name)
    schemas = db.get_collection("schemas")

    for module_name in listdir(path.dirname(__file__)):
        if str(module_name).startswith("m") and module_name.endswith(".py"):
            module_content = import_module(module_name[:-3])
            schema_version = {"_id": module_content.version}

            if await schemas.find_one(schema_version) is None:
                await module_content.upgrade(db)
                await schemas.insert_one(schema_version)


run(main())

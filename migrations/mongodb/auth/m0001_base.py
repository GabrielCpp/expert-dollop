from pymongo import DESCENDING, ASCENDING
from urllib.parse import urlsplit
from os import environ

version = "1"


async def upgrade(db):
    u = urlsplit(environ["DB_URL"])

    ressource = await db.create_collection("ressource")
    await ressource.create_index([("user_id", DESCENDING), ("kind", ASCENDING)])

    user = await db.create_collection("user")
    await user.create_index("id", unique=True)
    await user.create_index("email", unique=True)

    await db.command(
        "createUser",
        u.username,
        pwd=u.password,
        roles=["readWrite", "dbAdmin", "dbOwner"],
    )

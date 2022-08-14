from pymongo import DESCENDING, ASCENDING
from os import environ

version = "1"


async def upgrade(db):
    ressource = await db.create_collection("ressource")
    await ressource.create_index([("organization_id", DESCENDING), ("kind", ASCENDING)])

    user = await db.create_collection("user")
    await user.create_index("id", unique=True)
    await user.create_index("email", unique=True)

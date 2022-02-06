from asyncio import run
from pymongo import DESCENDING, ASCENDING
from os import environ
from urllib.parse import urlsplit, urlunsplit
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
u = urlsplit(environ["RESSOURCE_DB_URL"])
db_name = u.path.strip(" /")
c = urlunsplit((u.scheme, u.netloc, "admin", u.query, u.fragment))


async def upgrade():
    client = AsyncIOMotorClient(str(c))
    db = client.get_database(db_name)

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


run(upgrade())
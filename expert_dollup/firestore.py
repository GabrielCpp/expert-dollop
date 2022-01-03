import os
from asyncio import run
from google.cloud import firestore
from google.auth.credentials import AnonymousCredentials
from pydantic import BaseModel, Field
from typing import Optional

os.environ["FIRESTORE_EMULATOR_HOST"] = "127.0.0.1:8806"
credentials = AnonymousCredentials()
db = firestore.AsyncClient(project="my-project", credentials=credentials)


class City(BaseModel):
    name: str
    state: Optional[str]
    country: str
    capital: bool = False
    population: int = 0
    regions: list = Field(default_factory=list)


async def main():
    # Add a new document
    cities_ref = db.collection("cities")
    await cities_ref.document("BJ").set(
        City(
            name="Beijing",
            state=None,
            country="China",
            capital=True,
            population=21500000,
            regions=["hebei"],
        ).dict()
    )
    await cities_ref.document("SF").set(
        City(
            name="San Francisco",
            state="CA",
            country="USA",
            capital=False,
            population=860000,
            regions=["west_coast", "norcal"],
        ).dict()
    )
    await cities_ref.document("LA").set(
        City(
            name="Los Angeles",
            state="CA",
            country="USA",
            capital=False,
            population=3900000,
            regions=["west_coast", "socal"],
        ).dict()
    )
    await cities_ref.document("DC").set(
        City(
            name="Washington D.C.",
            state=None,
            country="USA",
            capital=True,
            population=680000,
            regions=["east_coast"],
        ).dict()
    )
    await cities_ref.document("TOK").set(
        City(
            name="Tokyo",
            state=None,
            country="Japan",
            capital=True,
            population=9000000,
            regions=["kanto", "honshu"],
        ).dict()
    )

    query_ref = cities_ref.where(u"country", u"==", u"USA").where(u"state", u"!=", None)

    async for doc in query_ref.stream():
        print(u"{} => {}".format(doc.id, doc.to_dict()))

    print()

    query_ref = cities_ref.where(u"state", u"==", u"CA").where(
        u"population", u"<", 1000000
    )

    async for doc in query_ref.stream():
        print(u"{} => {}".format(doc.id, doc.to_dict()))

    print()

    async for doc in db.collection(u"cities").stream():
        print(u"{} => {}".format(doc.id, doc.to_dict()))


run(main())
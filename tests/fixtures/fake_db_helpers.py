from collections import defaultdict
from typing import Callable, List, Dict, Type, TypeVar, Union
from injector import Injector
from inspect import isclass
from shutil import rmtree
from pydantic.main import BaseModel
from expert_dollup.shared.database_services import DbConnection
from expert_dollup.shared.database_services.adapter_interfaces import CollectionService

Domain = TypeVar("Domain")


class FakeDb:
    def __init__(self):
        self.collections: Dict[Type, List[object]] = defaultdict(list)

    def all(self, object_type: Type[Domain]) -> List[Domain]:
        return self.collections[object_type]

    def get_only_one(self, object_type: Type) -> object:
        assert object_type in self.collections
        objects = self.collections[object_type]
        assert len(objects) == 1

        return objects[0]

    def get_only_one_matching(
        self, object_type: Type[Domain], predicate: Callable[[object], bool]
    ) -> Domain:
        objects = self.collections[object_type]
        results = [
            matching_object
            for matching_object in objects
            if predicate(matching_object) is True
        ]
        assert len(results) == 1
        return results[0]

    def add(self, *args: Domain) -> Union[Domain, List[Domain]]:
        first_object = args[0]
        self.collections[type(first_object)].extend(args)
        return first_object if len(args) == 1 else args

    def merge(self, other: "FakeDb") -> None:
        for object_type, objects in other.collections.items():
            self.collections[object_type].extend(objects)


class DbFixtureHelper:
    @staticmethod
    def _insert_many(service, objects):
        async def do_inserts():
            await service.insert_many(objects)

        return do_inserts

    def __init__(self, injector: Injector, dal: DbConnection, auth_db: DbConnection):
        self.injector: Injector = injector
        self.dal = dal
        self.auth_db = auth_db
        self.db = None

    async def insert_daos(self, service_type: Type, daos: List[BaseModel]):
        service = self.injector.get(service_type)
        await service._impl.bulk_insert(daos)

    async def reset(self):
        await self.dal.truncate_db()
        await self.auth_db.truncate_db()
        rmtree("/tmp/expertdollup", ignore_errors=True)

    async def init_db(self, fake_db: FakeDb):
        async def do_init():
            await self.reset()

            for domain_type, objects in fake_db.collections.items():
                service_type = CollectionService[domain_type]
                service = self.injector.get(service_type)
                await service.insert_many(objects)

        await self.auth_db.transaction(do_init)
        self.db = fake_db

    async def load_fixtures(self, *build_db_slices: Callable[[], FakeDb]) -> FakeDb:
        db = self.db or FakeDb()

        for build_db_slice in build_db_slices:
            db.merge(build_db_slice())

        await self.init_db(db)
        return db

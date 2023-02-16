from collections import defaultdict
from typing import Callable, List, Dict, Type, TypeVar, Union, Optional
from typing_extensions import TypeAlias
from expert_dollup.shared.starlette_injection import Injector
from inspect import isclass
from shutil import rmtree
from pydantic.main import BaseModel
from expert_dollup.shared.database_services import DbConnection
from expert_dollup.shared.database_services.adapter_interfaces import Repository

Domain = TypeVar("Domain")
FakeDbLoader: TypeAlias = Callable[["FakeDb"], None]


class FakeDb:
    @staticmethod
    def create_from(loaders: List[FakeDbLoader]) -> "FakeDb":
        return FakeDb.load_into(None, loaders)

    @staticmethod
    def load_into(db: Optional["FakeDb"], loaders: List[FakeDbLoader]) -> "FakeDb":
        db = db or FakeDb()

        for load_objects in loaders:
            load_objects(db)

        return db

    def __init__(self):
        self.collections: Dict[Type, List[object]] = defaultdict(list)

    def all(self, object_type: Type[Domain]) -> List[Domain]:
        return self.collections[object_type]

    def all_match(
        self, object_type: Type[Domain], predicate: Callable[[object], bool]
    ) -> List[Domain]:
        objects = self.collections[object_type]
        results = [
            matching_object
            for matching_object in objects
            if predicate(matching_object) is True
        ]
        return results

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

    def get_by_name(self, object_type: Type[Domain], name: str) -> Domain:
        objects = self.collections[object_type]
        results = [
            matching_object
            for matching_object in objects
            if matching_object.name == name
        ]
        assert len(results) == 1
        return results[0]

    def add(self, *args: Domain) -> Union[Domain, List[Domain]]:
        if len(args) == 0:
            raise Exception("Add at lead one object")

        first_object = args[0]
        self.collections[type(first_object)].extend(args)
        return first_object if len(args) == 1 else args

    def add_all(self, domains: List[Domain]) -> List[Domain]:
        if len(domains) == 0:
            return []

        first_object = domains[0]
        self.collections[type(first_object)].extend(domains)
        return domains

    def merge(self, other: "FakeDb") -> None:
        for object_type, objects in other.collections.items():
            self.collections[object_type].extend(objects)


class DbFixtureHelper:
    @staticmethod
    def _insert_many(service, objects):
        async def do_inserts():
            await service.inserts(objects)

        return do_inserts

    def __init__(self, injector: Injector, dal: DbConnection, auth_db: DbConnection):
        self.injector = injector
        self.dal = dal
        self.auth_db = auth_db
        self.db = None

    async def reset(self):
        await self.dal.truncate_db()
        await self.auth_db.truncate_db()
        rmtree("/tmp/expertdollup", ignore_errors=True)

    async def init_db(self, fake_db: FakeDb) -> FakeDb:
        await self.reset()

        for domain_type, objects in fake_db.collections.items():
            service_type = Repository[domain_type]
            service = self.injector.get(service_type)
            await service.inserts(objects)

        self.db = fake_db
        return fake_db

    async def load_fixtures(self, *loaders: FakeDbLoader) -> FakeDb:
        db = FakeDb.load_into(self.db, loaders)
        db = await self.init_db(db)
        return db

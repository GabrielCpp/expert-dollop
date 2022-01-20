from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Callable, List, Dict, Any, Type
from injector import Injector
from inspect import isclass
from shutil import rmtree
from pydantic.main import BaseModel
from expert_dollup.infra import services
from expert_dollup.infra.storage_connectors.storage_client import StorageClient
from expert_dollup.shared.database_services import DbConnection


class FakeDb:
    def __init__(self):
        self.collections: Dict[Type, List[object]] = defaultdict(list)

    def all(self, object_type: Type) -> List[object]:
        return self.collections[object_type]

    def get_only_one(self, object_type: Type) -> object:
        assert object_type in self.collections
        objects = self.collections[object_type]
        assert len(objects) == 1

        return objects[0]

    def get_only_one_matching(
        self, object_type: Type, predicate: Callable[[object], bool]
    ) -> object:
        objects = self.collections[object_type]
        results = [
            matching_object
            for matching_object in objects
            if predicate(matching_object) is True
        ]
        assert len(results) == 1
        return results[0]

    def add(self, *args) -> object:
        first_object = args[0]
        self.collections[type(first_object)].extend(args)
        return first_object if len(args) == 1 else args

    def merge(self, other: "FakeDb") -> None:
        for object_type, objects in other.collections.items():
            self.collections[object_type].extend(objects)


class DbFixtureGenerator(ABC):
    @property
    @abstractmethod
    def db() -> FakeDb:
        pass

    @abstractmethod
    def generate(self) -> None:
        pass


class DbFixtureHelper:
    def __init__(self, injector: Injector, dal: DbConnection):
        self.injector: Injector = injector
        self.dal = dal
        self.services_by_domain: Dict[Type, Type] = {}

    def load_services(self, services) -> "DbFixtureHelper":
        for class_type in services.__dict__.values():
            if isclass(class_type):
                self.services_by_domain[class_type.Meta.domain] = class_type

        return self

    async def insert_daos(self, service_type: Type, daos: List[BaseModel]):
        service = self.injector.get(service_type)
        await service._impl.bulk_insert(daos)

    async def init_db(self, fake_db: FakeDb):
        await self.dal.truncate_db()
        rmtree("/tmp/expertdollup", ignore_errors=True)

        for domain_type, objects in fake_db.collections.items():
            assert (
                domain_type in self.services_by_domain
            ), f"No service for domain {domain_type.__name__}"
            service_type = self.services_by_domain[domain_type]
            service = self.injector.get(service_type)
            await service.insert_many(objects)

    async def load_fixtures(
        self, *generator_types: List[Type[DbFixtureGenerator]]
    ) -> FakeDb:
        db = FakeDb()

        for generator_type in generator_types:
            generator = generator_type()
            generator.generate()
            db.merge(generator.db)

        await self.init_db(db)
        return db

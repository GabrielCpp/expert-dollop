from typing import Callable, TypeVar, List, Type, Optional, Protocol, Dict, Any
from pydantic import BaseModel


class DictLike(Protocol):
    def _asdict() -> dict:
        pass


Domain = TypeVar("Domain")


class CollectionMapper:
    def __init__(
        self,
        mapper,
        domain: Type[Domain],
        dao: Type,
        latest_version: Optional[int],
        version_mappers,
    ):
        self._mapper = mapper
        self._domain = domain
        self._dao = dao
        self._version = latest_version
        self._version_mappers = version_mappers

    def map_to_dict(self, domain: Domain) -> dict:
        dao = self._mapper.map(domain, self._dao)
        d = self.add_version_to_dao(dao)

        return d

    def map_many_to_dict(self, domains: List[Domain]) -> List[dict]:
        dicts = self._mapper.map_many(domains, self._dao, after=self.add_version_to_dao)
        return dicts

    def map_to_domain(self, record: DictLike) -> Domain:
        dao = self.remap_record_to_lastest(record._asdict())
        result = self._mapper.map(dao, self._domain)
        return result

    def map_many_to_domain(self, records: List[DictLike]) -> List[Domain]:
        daos = [self.remap_record_to_lastest(record._asdict()) for record in records]
        results = self._mapper.map_many(daos, self._domain)
        return results

    def remap_record_to_lastest(self, record: dict) -> dict:
        version = record.get("_version", None)

        if version is None or version == self._version:
            return self._dao.parse_obj(record)

        return self._version_mappers[version][self._version](
            self._version_mappers, record
        )

    def add_version_to_dao(self, dao: BaseModel) -> dict:
        d = dao.dict()

        if not self._version is None:
            d["_version"] = self._version

        return d

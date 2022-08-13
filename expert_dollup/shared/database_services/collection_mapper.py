from typing import TypeVar, List, Type, Optional, Dict
from pydantic import BaseModel


Domain = TypeVar("Domain")
Record = TypeVar("Record")


class CollectionMapper:
    def __init__(
        self,
        mapper,
        domain: Type[Domain],
        dao: Type,
        latest_version: Optional[int],
        version_mappers,
        dao_to_dict: callable = lambda dao: dao.dict(),
        record_to_dict: callable = lambda x: x,
    ):
        self._mapper = mapper
        self._domain = domain
        self._dao = dao
        self._version = latest_version
        self._version_mappers = version_mappers
        self._to_dao = dao_to_dict
        self._record_to_dict = record_to_dict

    def map_to_dict(self, domain: Domain) -> dict:
        dao = self._mapper.map(domain, self._dao)
        d = self.add_version_to_dao(dao)

        return d

    def map_many_to_dict(self, domains: List[Domain]) -> List[dict]:
        dicts = self._mapper.map_many(domains, self._dao, after=self.add_version_to_dao)
        return dicts

    def map_to_domain(self, record: Record) -> Domain:
        dao = self.remap_record_to_lastest(record)
        result = self._mapper.map(dao, self._domain)
        return result

    def map_many_to_domain(self, records: List[Record]) -> List[Domain]:
        daos = [self.remap_record_to_lastest(record) for record in records]
        results = self._mapper.map_many(daos, self._domain)
        return results

    def remap_record_to_lastest(self, record: Record) -> dict:
        d = self._record_to_dict(record)
        version = d.get("_version", None)

        if not version is None and version != self._version:
            d = self._version_mappers[version][self._version](self._version_mappers, d)

        return self._dao.parse_obj(d)

    def add_version_to_dao(self, dao: BaseModel) -> dict:
        d = self._to_dao(dao)

        if not self._version is None:
            d["_version"] = self._version

        return d

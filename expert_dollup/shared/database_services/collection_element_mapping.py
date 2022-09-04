from typing import TypeVar, List, Type, Optional, Dict, Callable, Any, Iterable
from pydantic import BaseModel
from expert_dollup.shared.automapping import Mapper

Domain = TypeVar("Domain")
Record = TypeVar("Record")


class CollectionElementMapping:
    def __init__(
        self,
        mapper: Mapper,
        domain: Type[Domain],
        dao: Type,
        latest_version: Optional[int],
        version_mappers,
        type_of: Optional[str],
        dao_to_dict: Callable[[BaseModel], dict] = lambda dao: dao.dict(),
        record_to_dict: Callable[[Any], dict] = lambda x: x,
    ):
        self._mapper = mapper
        self._domain = domain
        self._dao = dao
        self._version = latest_version
        self._version_mappers = version_mappers
        self._type_of = type_of
        self._dao_to_dict = dao_to_dict
        self._record_to_dict = record_to_dict

    def map_to_dict(self, domain: Domain) -> dict:
        dao = self._mapper.map(domain, self._dao)
        d = self._map_dao_to_dict(dao)

        return d

    def map_many_to_dict(self, domains: List[Domain]) -> List[dict]:
        dicts = self._mapper.map_many(domains, self._dao, after=self._map_dao_to_dict)
        return dicts

    def map_many_dao_to_dict(self, daos: List[BaseModel]) -> Iterable[dict]:
        dicts = (self._map_dao_to_dict(dao) for dao in daos)
        return dicts

    def map_domain_to_dao(self, domain: Domain) -> BaseModel:
        return self._mapper.map(domain, self._dao)

    def map_to_domain(self, record: Record) -> Domain:
        dao = self._remap_record_to_lastest(record)
        result = self._mapper.map(dao, self._domain)
        return result

    def map_many_to_domain(self, records: List[Record]) -> List[Domain]:
        daos = [self._remap_record_to_lastest(record) for record in records]
        results = self._mapper.map_many(daos, self._domain)
        return results

    def _remap_record_to_lastest(self, record: Record) -> dict:
        d = self._record_to_dict(record)
        version = d.get("_version", None)

        if not version is None and version != self._version:
            d = self._version_mappers[version][self._version](self._version_mappers, d)

        return self._dao.parse_obj(d)

    def _map_dao_to_dict(self, dao: BaseModel) -> dict:
        d = self._dao_to_dict(dao)

        if not self._version is None:
            d["_version"] = self._version

        if not self._type_of is None:
            d["_type"] = self._type_of(dao)

        return d

from typing import (
    TypeVar,
    List,
    Type,
    Optional,
    Dict,
    Callable,
    Any,
    Iterable,
    get_args,
)
from pydantic import BaseModel
from dataclasses import dataclass, field
from expert_dollup.shared.automapping import Mapper


Domain = TypeVar("Domain")
Record = TypeVar("Record")


@dataclass
class DaoVersioning:
    latest_version: int = -1
    version_mappers: Dict[int, Dict[int, Callable[[dict], dict]]] = field(
        default_factory=dict
    )

    def map_to_latest(self, d: dict, version_field: str) -> dict:
        if self.latest_version <= 0:
            return d

        version = d[version_field]

        if version != self.latest_version:
            return versioning.version_mappers[version][self.latest_version](d)

        return d

    def add_version(self, d: dict, version_field: str) -> None:
        if self.latest_version > 0:
            d[version_field] = self.latest_version


@dataclass
class DaoTypeAnnotation:
    kind: str = ""
    is_my_kind: Callable[[dict], bool] = lambda _: False

    def add_kind(self, d: dict, kind_field: str) -> None:
        if self.kind != "":
            d[kind_field] = self.kind


@dataclass
class DaoMultiMapping:
    kinds: Dict[str, "DaoMappingDetails"]

    def kind_of(self, d: dict) -> "DaoMappingDetails":
        return self.kinds[self.type_of(d)]

    def type_of(self, d: dict) -> str:
        for mapping_details in self.kinds.values():
            if mapping_details.typed.is_my_kind(d):
                return mapping_details.typed.kind

        raise Exception("No matching type found")


@dataclass
class DaoMappingConfig:
    versioning: DaoVersioning = field(default_factory=DaoVersioning)
    typed: DaoTypeAnnotation = field(default_factory=DaoTypeAnnotation)


@dataclass
class DaoMappingDetails:
    domain: Type
    dao: Type
    versioning: DaoVersioning = field(default_factory=DaoVersioning)
    typed: DaoTypeAnnotation = field(default_factory=DaoTypeAnnotation)
    multi_map: Optional[DaoMultiMapping] = None

    def mapping_for(self, d: dict) -> "DaoMappingDetails":
        if self.multi_map is None:
            return self

        return self.multi_map.kind_of(d)

    def domain_to_dao(self, domain):
        if self.multi_map is None:
            return self.dao

        domain_type = type(domain)

        return next(
            details.dao
            for details in self.multi_map.kinds.values()
            if details.domain is domain_type
        )

    def dao_to_domain(self, dao):
        if self.multi_map is None:
            return self.domain

        dao_type = type(dao)

        return next(
            details.domain
            for details in self.multi_map.kinds.values()
            if details.dao is dao_type
        )


class CollectionElementMapping:
    @staticmethod
    def get_mapping_details(domain: Type, dao: Type):
        daos = get_args(dao)
        domains = get_args(domain)
        assert len(daos) == len(domains)

        if len(daos) == 0:
            config = getattr(
                dao.Meta,
                "dao_mapping_details",
                DaoMappingConfig(),
            )

            return DaoMappingDetails(
                domain=domain, dao=dao, versioning=config.versioning, typed=config.typed
            )

        return DaoMappingDetails(
            dao=dao,
            domain=domain,
            multi_map=DaoMultiMapping(
                kinds={
                    dao.Meta.dao_mapping_details.typed.kind: CollectionElementMapping.get_mapping_details(
                        domain, dao
                    )
                    for domain, dao in zip(domains, daos)
                }
            ),
        )

    def __init__(
        self,
        mapper: Mapper,
        mapping_details: DaoMappingDetails,
        dao_to_dict: Callable[[BaseModel], dict] = lambda dao: dao.dict(),
        record_to_dict: Callable[[Any], dict] = lambda x: x,
    ):
        self._mapper = mapper
        self._mapping_details = mapping_details
        self._dao_to_dict = dao_to_dict
        self.map_record_to_dict = record_to_dict

    def map_domain_to_dao(self, domain: Domain) -> BaseModel:
        dao_type = self._mapping_details.domain_to_dao(domain)
        return self._mapper.map(domain, dao_type)

    def map_domain_to_dict(self, domain: Domain) -> dict:
        dao_type = self._mapping_details.domain_to_dao(domain)
        dao = self._mapper.map(domain, dao_type)
        d = self.map_dao_to_dict(dao)
        return d

    def map_dao_to_domain(self, dao: BaseModel) -> Domain:
        domain_type = self._mapping_details.dao_to_domain(dao)
        domain = self._mapper.map(dao, domain_type)
        return domain

    def map_dao_to_dict(self, dao: BaseModel) -> dict:
        d = self._dao_to_dict(dao)
        mapping = self._mapping_details.mapping_for(d)
        mapping.versioning.add_version(d, "_version")
        mapping.typed.add_kind(d, "_type")
        return d

    def map_record_to_domain(self, record: Record) -> Domain:
        dao = self.map_record_to_dao(record)
        domain_type = self._mapping_details.dao_to_domain(dao)
        result = self._mapper.map(dao, domain_type)
        return result

    def map_record_to_dao(self, record: Record) -> BaseModel:
        d = self.map_record_to_dict(record)
        mapping = self._mapping_details.mapping_for(d)
        d = mapping.versioning.map_to_latest(d, "_version")
        return mapping.dao.parse_obj(d)

    def map_many_domain_to_dict(self, domains: List[Domain]) -> List[dict]:
        return [self.map_domain_to_dict(domain) for domain in domains]

    def map_many_dao_to_dict(self, daos: List[BaseModel]) -> Iterable[dict]:
        return (self.map_dao_to_dict(dao) for dao in daos)

    def map_many_record_to_domain(self, records: List[Record]) -> List[Domain]:
        return [self.map_record_to_domain(record) for record in records]

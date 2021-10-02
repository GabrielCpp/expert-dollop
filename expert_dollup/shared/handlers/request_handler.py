from typing import Type, Optional, List
from dataclasses import dataclass
from ..automapping import Mapper


@dataclass
class MappingChain:
    dto: Optional[Type] = None
    domain: Optional[Type] = None
    out_domain: Optional[Type] = None
    out_dto: Optional[Type] = None


class RequestHandler:
    def __init__(self, mapper: Mapper):
        self.mapper = mapper

    async def handle(self, usecase, query_dto, mapping_chain: MappingChain):
        query_domain = query_dto

        if not mapping_chain.dto is None:
            query_domain = self.mapper.map(
                query_dto, mapping_chain.domain, mapping_chain.dto
            )

        result = await usecase(query_domain)

        if not mapping_chain.out_dto is None:
            result = self.mapper.map(
                result, mapping_chain.out_dto, mapping_chain.out_domain
            )

        return result

    async def handle_many(self, usecase, query_dto, mapping_chain: MappingChain):
        query_domain = query_dto

        if not mapping_chain.dto is None:
            query_domain = self.mapper.map(
                query_dto, mapping_chain.domain, mapping_chain.dto
            )

        result = await usecase(query_domain)

        if not mapping_chain.out_dto is None:
            result = self.mapper.map_many(
                result, mapping_chain.out_dto, mapping_chain.out_domain
            )

        return result

    async def forward(self, usecase, params, mapping_chain: MappingChain):
        result = await usecase(**params)

        if not mapping_chain.out_dto is None:
            result = self.mapper.map(
                result, mapping_chain.out_dto, mapping_chain.out_domain
            )

        return result

    async def forward_many(self, usecase, params, mapping_chain: MappingChain):
        result = await usecase(**params)

        if not mapping_chain.out_dto is None:
            result = self.mapper.map_many(
                result, mapping_chain.out_dto, mapping_chain.out_domain
            )

        return result

    async def forward_mapped(
        self, usecase, params, mapping_chain: MappingChain, map_keys={}
    ):
        for key, mapping in map_keys.items():
            if getattr(mapping.domain, "__origin__", None) is list:
                params[key] = self.mapper.map_many(
                    params[key],
                    mapping.domain.__args__[0],
                    mapping.dto and mapping.dto.__args__[0],
                )
            else:
                params[key] = self.mapper.map(params[key], mapping.domain, mapping.dto)

        result = await usecase(**params)
        import jsonpickle

        with open("test.json", "w") as f:
            f.write(jsonpickle.encode(result))

        if not mapping_chain.out_dto is None:
            if getattr(mapping_chain.out_dto, "__origin__", None) is list:
                result = self.mapper.map_many(
                    result,
                    mapping_chain.out_dto.__args__[0],
                    mapping_chain.out_domain and mapping_chain.out_domain.__args__[0],
                )
            else:
                result = self.mapper.map(
                    result, mapping_chain.out_dto, mapping_chain.out_domain
                )

        return result

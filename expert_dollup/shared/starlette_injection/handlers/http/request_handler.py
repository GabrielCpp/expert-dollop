from typing import Type, Optional, List
from ..interfaces import MappingChain
from ....automapping import Mapper


class RequestHandler:
    def __init__(self, mapper: Mapper):
        self.mapper = mapper

    async def do_handle(
        self,
        usecase,
        query_dto,
        result_mapping: Optional[MappingChain] = None,
        **kwargs: Dict[str, MappingChain]
    ):
        mapped_kwargs = {
            name: self._do_mapping(value) for name, value in kwargs.items()
        }

        result = await usecase(**mapped_kwargs)

        if not result_mapping is None:
            result = self._do_mapping(
                MappingChain(
                    value=result, dto=result_mapping.dto, domain=result_mapping.domain
                ),
                True,
            )

        return result

    def _do_mapping(self, src, is_reversed=False):
        if isinstance(src, MappingChain):
            if is_reversed:
                in_type = src.domain
                out_type = src.dto
            else:
                in_type = src.dto
                out_type = src.domain

            if getattr(out_type, "__origin__", None) is list:
                return self.mapper.map_many(
                    result,
                    out_type.__args__[0],
                    in_type and in_type.__args__[0],
                )
            else:
                return self.mapper.map(src.value, out_type, in_type)

        return src

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

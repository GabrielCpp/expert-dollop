from ..automapping import Mapper


class RequestHandler:
    def __init__(self, mapper: Mapper):
        self.mapper = mapper

    async def handle(self, query_dto, QueryDto, QueryDomain, usecase):
        query_domain = self.mapper.map(query_dto, QueryDomain, QueryDto)
        await usecase(query_domain)

    async def handle_id_with_result(self, id, usecase, ResultDto):
        result = await usecase(id)
        result_dto = self.mapper.map(result, ResultDto)
        return result_dto

    async def handle_with_result(self, query_dto, QueryDto, QueryDomain, usecase, ResultDto):
        query_domain = self.mapper.map(query_dto, QueryDomain, QueryDto)
        result = await usecase(query_domain)
        result_dto = self.mapper.map(result, ResultDto)
        return result_dto

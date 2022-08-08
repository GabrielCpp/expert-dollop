from expert_dollup.infra.expert_dollup_storage import (
    ExpertDollupStorage,
    ReportRowDictDao,
    ReportRowsCacheDao,
)
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.domains import ReportRowsCache, ReportRowKey, ReportRowDict
from expert_dollup.shared.automapping import Mapper
from pydantic import BaseModel


class RootRowsDao(BaseModel):
    __root__: ReportRowsCacheDao


class ReportDefinitionRowCacheCloudObject(ObjectStorage[ReportRowsCache, ReportRowKey]):
    def __init__(self, storage: ExpertDollupStorage, mapper: Mapper):
        self.storage = storage
        self.mapper = mapper

    async def save(self, ctx: ReportRowKey, rows: ReportRowsCache):
        path = self.get_url(ctx)
        daos = self.mapper.map_many(rows, ReportRowDictDao, ReportRowDict)
        await self.storage.upload_binary(
            path,
            RootRowsDao(__root__=daos).json().encode("utf8"),
        )

    async def load(self, ctx: ReportRowKey) -> ReportRowsCache:
        path = self.get_url(ctx)
        rows_cache_json = await self.storage.download_binary(path)
        rows_cache = RootRowsDao.parse_raw(rows_cache_json.decode("utf8"))
        domains = self.mapper.map_many(
            rows_cache.__root__, ReportRowDict, ReportRowDictDao
        )

        return domains

    def get_url(self, ctx: ReportRowKey) -> str:
        return f"project_definitions/{ctx.project_definition_id}/report_definitions/{ctx.report_definition_id}/rows_cache.json.gzip"

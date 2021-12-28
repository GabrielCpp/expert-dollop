from expert_dollup.shared.database_services import JsonSerializer
from expert_dollup.infra.expert_dollup_storage import ExpertDollupStorage
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.domains import ReportRowsCache, ReportRowKey


class ReportDefinitionRowCacheCloudObject(ObjectStorage[ReportRowsCache, ReportRowKey]):
    def __init__(self, storage: ExpertDollupStorage):
        self.storage = storage

    async def save(self, ctx: ReportRowKey, rows: ReportRowsCache):
        await self.storage.upload_binary(
            f"project_definitions/{ctx.project_def_id}/report_definition/{ctx.report_definition_id}/rows_cache.json.gzip",
            JsonSerializer.encode(rows, indent=None).encode("utf8"),
        )

    async def load(self, ctx: ReportRowKey) -> ReportRowsCache:
        rows_cache_json = await self.storage.download_binary(
            f"project_definitions/{ctx.project_def_id}/report_definition/{ctx.report_definition_id}/rows_cache.json.gzip",
        )

        rows_cache = JsonSerializer.decode(rows_cache_json.decode("utf8"))

        return rows_cache

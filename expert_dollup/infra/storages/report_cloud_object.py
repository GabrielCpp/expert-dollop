from expert_dollup.infra.expert_dollup_storage import ExpertDollupStorage, ReportDao
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.domains import Report, ReportKey
from expert_dollup.shared.automapping import Mapper


class ReportCloudObject(ObjectStorage[Report, ReportKey]):
    def __init__(self, storage: ExpertDollupStorage, mapper: Mapper):
        self.storage = storage
        self.mapper = mapper

    async def save(self, ctx: ReportKey, report: Report):
        path = self.get_url(ctx)
        dao = self.mapper.map(report, ReportDao)
        await self.storage.upload_binary(
            path,
            dao.json().encode("utf8"),
        )

    async def load(self, ctx: ReportKey) -> Report:
        path = self.get_url(ctx)
        report_json = await self.storage.download_binary(path)

        report_dao = ReportDao.parse_raw(report_json.decode("utf8"))
        report = self.mapper.map(report_dao, Report)

        return report

    def get_url(self, ctx: ReportKey) -> str:
        return f"projects/{ctx.project_id}/reports/{ctx.report_definition_id}.json.gzip"
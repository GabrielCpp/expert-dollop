from gzip import GzipFile
from io import BytesIO
from expert_dollup.infra.expert_dollup_storage import (
    ExpertDollupStorage,
    StagedFormulaDao,
)
from expert_dollup.core.object_storage import ObjectStorage
from expert_dollup.core.domains import StagedFormulas, StagedFormulasKey, StagedFormula
from expert_dollup.shared.automapping import Mapper
from expert_dollup.shared.database_services import JsonSerializer


class StagedFormulaCache(ObjectStorage[StagedFormulas, StagedFormulasKey]):
    def __init__(self, storage: ExpertDollupStorage, mapper: Mapper):
        self.storage = storage
        self.mapper = mapper

    async def save(self, ctx: StagedFormulasKey, staged_formulas: StagedFormulas):
        fileobj = BytesIO()
        path = self.get_url(ctx)
        daos = self.mapper.map_many(staged_formulas, StagedFormulaDao)

        with GzipFile(fileobj=fileobj, compresslevel=9, mode="wb") as f:
            for dao in daos:
                f.write(JsonSerializer.encode(dao.dict()))
                f.write(b"\n")

        fileobj.seek(0)
        output_bytes = fileobj.read()
        await self.storage.upload_binary(path, output_bytes)

    async def load(self, ctx: StagedFormulasKey) -> StagedFormulas:
        daos = []
        path = self.get_url(ctx)
        initial_bytes = await self.storage.download_binary(path)
        inbytes = BytesIO(initial_bytes)

        with GzipFile(fileobj=inbytes, mode="rb") as f:
            for line in f.readlines():
                dao = StagedFormulaDao.parse_obj(JsonSerializer.decode(line))
                daos.append(dao)

        domains = self.mapper.map_many(daos, StagedFormula)

        return domains

    def get_url(self, ctx: StagedFormulasKey) -> str:
        return f"project_definitions/{ctx.project_definition_id}/staged_formulas.jsonl.gzip"

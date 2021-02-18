from .mapping_helpers import (
    map_dao_to_dto,
    normalize_request_results,
    normalize_dtos,
    unwrap,
    unwrap_many,
)

from .fake_db_helpers import (
    FakeExpertDollupDb,
    DbSetupHelper,
    populate_db,
)

from .factories_dto import (
    ProjectDefinitionDtoFactory,
    ProjectDefinitionContainerDtoFactory,
    TranslationDtoFactory,
    ProjectDtoFactory,
    FormulaDtoFactory,
)

from .object_dump_helpers import dump_to_file, set_dump_path, dump_snapshot, jsonify

from .generators import SimpleProject, MiniProject


class FlowRunner:
    def __init__(self):
        self.steps = []

    def step(self, func):
        self.steps.append(func)
        return self

    async def run(self, *args):
        params = args

        for step in self.steps:
            params = await step(*params)

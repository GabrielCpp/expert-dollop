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
    DatasheetDefinitionDtoFactory,
    DatasheetDefinitionElementDtoFactory,
    LabelCollectionDtoFactory,
    LabelDtoFactory,
    DatasheetDtoFactory,
)

from .object_dump_helpers import dump_to_file, set_dump_path, dump_snapshot, jsonify

from .generators import *
from .rest_cursors import AsyncCursor


class FlowRunner:
    def __init__(self):
        self.steps = []

    def step(self, func: callable):
        self.steps.append(func)
        return self

    def extend(self, runner: "FlowRunner"):
        self.steps.extend(runner.steps)

    async def run(self, *args):
        params = args

        for step in self.steps:
            new_params = await step(*params)

            if isinstance(new_params, tuple):
                params = new_params
            else:
                params = []

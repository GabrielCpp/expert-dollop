from expert_dollup.app.modules import build_container
from expert_dollup.shared.automapping import Mapper
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from tests.fixtures import *


"""
def to_dto(tables: FakeExpertDollupDb, mapper: Mapper) -> FakeExpertDollupDbDto:
    def double_map(data, current_type, domain_type, dto_type):
        return mapper.map_many(
            mapper.map_many(data, domain_type, current_type), dto_type
        )

    return TablesDto(
        project_definitions=double_map(
            tables.project_definitions,
            ProjectDefinitionDao,
            ProjectDefinition,
            ProjectDefinitionDto,
        ),
        project_definition_nodes=double_map(
            tables.project_definition_nodes,
            ProjectDefinitionNodeDao,
            ProjectDefinitionNode,
            ProjectDefinitionNodeDto,
        ),
        translations=double_map(
            tables.translations, TranslationDao, Translation, TranslationDto
        ),
    )
"""


def generate_json(generate_layer, output_path=None):
    from injector import Injector
    from jsonpickle import encode, set_encoder_options, set_preferred_backend

    fixture = SimpleProject()
    fixture.generate()
    model = fixture.model

    if generate_layer == "dto":
        injector = build_container()
        mapper = injector.get(Mapper)
        model = to_dto(model, mapper)
    elif generate_layer != "dao":
        raise Exception(f"Unkown layer {generate_layer}")

    set_encoder_options("simplejson", sort_keys=True)
    set_preferred_backend("simplejson")
    json_content = encode(model, indent=4, unpicklable=False)

    if output_path is None:
        print(json_content)
    else:
        with open(output_path, "w") as f:
            f.write(json_content)


def fill_db():
    import os
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()
    injector = build_container()
    db_setup_helper = injector.get(DbSetupHelper)

    fixture = SimpleProject()
    fixture.generate()
    model = fixture.model

    async def main():
        async with injector.get(ExpertDollupDatabase) as _:
            await db_setup_helper.init_db(model)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

from expert_dollup.app.modules import build_container
from expert_dollup.infra.expert_dollup_db import ExpertDollupDatabase
from tests.fixtures import dump_snapshot
from tests.fixtures import *


def generate_json(generate_layer, output_path=None):
    fixture = SimpleProject()
    fixture.generate()

    if generate_layer != "dao":
        raise Exception(f"Unkown layer {generate_layer}")

    json_content = dump_snapshot(fixture.db)

    if output_path is None:
        print(json_content)
    else:
        with open(output_path, "w") as f:
            f.write(json_content)


def fill_db(model):
    import os
    import asyncio
    from dotenv import load_dotenv

    load_dotenv()
    injector = build_container()
    db_setup_helper = injector.get(DbFixtureHelper)

    async def main():
        async with injector.get(ExpertDollupDatabase) as _:
            await db_setup_helper.init_db(model)

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(main())
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


def load_simple_project():
    fixture = SimpleProject()
    fixture.generate()
    model = fixture.model
    fill_db(model)


def load_simple_datasheet_def():
    fixture = SimpleDatasheetDef()
    fixture.generate()
    model = fixture.model
    fill_db(model)

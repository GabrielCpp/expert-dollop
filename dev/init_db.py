from expert_dollup.app.modules import build_container
from expert_dollup.shared.automapping import Mapper
from tests.fixtures import FakeExpertDollupDb, SimpleProject


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
        project_definition_containers=double_map(
            tables.project_definition_containers,
            ProjectDefinitionContainerDao,
            ProjectDefinitionContainer,
            ProjectDefinitionContainerDto,
        ),
        translations=double_map(
            tables.translations, TranslationDao, Translation, TranslationDto
        ),
    )
"""


def generate_json(generate_layer, output_path=None):
    from injector import Injector

    fixture = SimpleProject()
    fixture.generate()
    model = fixture.model

    if generate_layer == "dto":
        injector = build_container()
        mapper = injector.get(Mapper)
        model = to_dto(model, mapper)
    elif generate_layer != "dao":
        raise Exception(f"Unkown layer {generate_layer}")

    json_content = model.json(indent=4, sort_keys=True)

    if output_path is None:
        print(json_content)
    else:
        with open(output_path, "w") as f:
            f.write(json_content)


def generate_sql():
    import os
    from dotenv import load_dotenv
    from sqlalchemy import create_engine

    load_dotenv()
    DATABASE_URL = "postgresql://{}:{}@{}/{}".format(
        os.environ["POSTGRES_USERNAME"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_DB"],
    )

    engine = create_engine(DATABASE_URL)
    injector = build_container()
    db_setup_helper = injector.get(DbSetupHelper)

    with engine.connect() as connection:
        fixture = SimpleProject()
        fixture.generate()
        model = fixture.model
        db_setup_helper.init_db(model, connection)

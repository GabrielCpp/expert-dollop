from .simple_project import SimpleProject
from .tables import insert, to_dto
from expert_dollup.app.modules import build_container
from expert_dollup.shared.automapping import Mapper


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

    with engine.connect() as connection:
        fixture = SimpleProject()
        fixture.generate()
        model = fixture.model
        insert(model, connection)

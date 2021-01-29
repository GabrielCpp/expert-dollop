import os
from dotenv import load_dotenv
from sqlalchemy import MetaData, create_engine


def truncate_db():
    load_dotenv()
    DATABASE_URL = "postgres://{}:{}@{}/{}".format(
        os.environ["POSTGRES_USERNAME"],
        os.environ["POSTGRES_PASSWORD"],
        os.environ["POSTGRES_HOST"],
        os.environ["POSTGRES_DB"],
    )

    engine = create_engine(DATABASE_URL)
    meta = MetaData(bind=engine, reflect=True)
    con = engine.connect()
    trans = con.begin()
    for table in meta.sorted_tables:
        con.execute(f'ALTER TABLE "{table.name}" DISABLE TRIGGER ALL;')
        con.execute(table.delete())
        con.execute(f'ALTER TABLE "{table.name}" ENABLE TRIGGER ALL;')
    trans.commit()

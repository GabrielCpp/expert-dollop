from invoke import task


@task
def start(c):
    c.run("poetry run uvicorn predykt.main:app --reload")


@task
def test(c, test=None):
    if test is None:
        c.run("poetry run pytest -v")
    else:
        print(f"poetry run pytest -k '{test}'")
        c.run(f"poetry run pytest -k '{test}'")


@task(name='migration:new')
def newMigration(c, message=None):
    if message is None:
        print("Message required")
        return

    c.run("poetry run alembic revision -m \"{}\"".format(message))


@task(name='migration:run')
def runMigration(c):
    c.run("poetry run alembic upgrade head")


@task(name='migration:sql')
def migrate(c, migration):
    c.run("poetry run alembic upgrade {} --sql".format(message))


@task
def initDb(c):
    c.run("poetry run python predykt/dev/init_db.py")


@task
def deleteDb(c):
    c.run("docker container stop postgres_data")
    c.run("docker rm postgres_data")
    c.run("docker volume rm postgres_data")


@task
def dbUp(c):
    c.run("docker-compose up --force-recreate --abort-on-container-exit --attach-dependencies adminer")


@task
def fixture(c, poetry=False):

    if poetry:
        from predykt.dev.init_db import generate_json
        generate_json()
    else:
        c.run("poetry run invoke fixture --poetry")

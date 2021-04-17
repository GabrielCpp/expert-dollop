from invoke import task


@task
def start(c):
    c.run("poetry run uvicorn expert_dollup.main:app --reload")


@task
def test(c, test=None):
    if test is None:
        c.run("poetry run pytest -v")
    else:
        print(f"poetry run pytest -k '{test}'")
        c.run(f"poetry run pytest -k '{test}'")


@task
def black(c):
    c.run("poetry run black .")


@task(name="migration:new")
def newMigration(c, message=None):
    if message is None:
        print("Message required")
        return

    c.run('poetry run alembic revision -m "{}"'.format(message))


@task(name="db:upgrade:head")
def runMigration(c):
    c.run("poetry run alembic upgrade head")


@task(name="db:upgrade")
def migrate(c, migration):
    c.run("poetry run alembic upgrade {} --sql".format(message))


@task(name="db:init")
def initDb(c):
    c.run("poetry run python dev/init_db.py")


@task(name="db:delete")
def deleteDb(c):
    if c.run("docker ps -aq").stdout != "":
        c.run("docker stop $(docker ps -aq)")

    if c.run("docker ps -aq").stdout != "":
        c.run("docker rm $(docker ps -aq)")

    c.run("docker network prune -f")

    if c.run("docker images --filter dangling=true -qa").stdout != "":
        c.run("docker rmi -f $(docker images --filter dangling=true -qa)")

    if c.run("docker volume ls --filter dangling=true -q").stdout != "":
        c.run("docker volume rm $(docker volume ls --filter dangling=true -q)")

    if c.run("docker images -qa").stdout != "":
        c.run("docker rmi -f $(docker images -qa)")


@task(name="db:up")
def dbUp(c):
    c.run(
        "docker-compose up --force-recreate --abort-on-container-exit --attach-dependencies adminer postgres"
    )


@task(name="db:fixture")
def fill_db_with_fixture(c, poetry=False):
    if poetry:
        from dev.init_db import fill_db
        from tests.fixtures import truncate_db

        truncate_db()
        fill_db()
    else:
        c.run("poetry run invoke db:fixture --poetry")


@task
def fixture(c, layer="dao", poetry=False):
    if poetry:
        from dev.init_db import generate_json

        generate_json(layer)
    else:
        c.run(f"poetry run invoke fixture --poetry --layer {layer}")


@task(name="db:truncate")
def truncate_db(c, poetry=False):
    if poetry:
        from tests.fixtures import truncate_db

        truncate_db()
    else:
        c.run("poetry run invoke db:truncate --poetry")

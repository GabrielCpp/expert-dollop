from invoke import task
from pathlib import Path
import base64
import os
import asyncio


def drop_db():
    from dotenv import load_dotenv
    from expert_dollup.shared.database_services import create_connection

    load_dotenv()
    connection = create_connection(os.getenv("DATABASE_URL"))
    asyncio.run(connection.drop_db())


def truncate_db():
    from dotenv import load_dotenv
    from expert_dollup.shared.database_services import create_connection

    load_dotenv()
    connection = create_connection(os.getenv("DATABASE_URL"))
    asyncio.run(connection.truncate_db())


@task(name="start-http")
def start_http(c):
    c.run(
        "poetry run uvicorn expert_dollup.main:app --reload --host 0.0.0.0 --port 8000"
    )


@task
def start(c):
    c.run(
        "poetry run uvicorn expert_dollup.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile .local/predykt.dev.key --ssl-certfile .local/predykt.dev.crt"
    )


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
    c.run("poetry run alembic upgrade {} --sql".format(migration))


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
    c.run("docker-compose up --force-recreate adminer postgres")


@task(name="db:fixture")
def fill_db_with_fixture(c, name, truncate=False, poetry=False):
    if poetry:
        from dev.init_db import load_simple_project, load_simple_datasheet_def
        from dotenv import load_dotenv
        from expert_dollup.shared.database_services import create_connection

        if truncate is True:
            truncate_db()

        if name == "simple_project":
            load_simple_project()
        elif name == "simple_datasheet_def":
            load_simple_datasheet_def()
        else:
            print(f"Unkown fixture {name}")
    else:
        c.run(
            f"poetry run invoke db:fixture --poetry --name={name} {'--truncate' if truncate else ''}"
        )


@task(name="db:truncate")
def db_truncate(c, poetry=False):
    if not poetry:
        c.run("poetry run invoke db:truncate --poetry")

    truncate_db()


@task(name="db:drop")
def db_drop(c, poetry=False):
    if not poetry:
        c.run("poetry run invoke db:drop --poetry")

    drop_db()


@task
def fixture(c, layer="dao", poetry=False):
    if poetry:
        from dev.init_db import generate_json

        generate_json(layer)
    else:
        c.run(f"poetry run invoke fixture --poetry --layer {layer}")


def generate_cert(c, folder: Path, domain_name: str, ca_name: str = "myCA"):
    folder.mkdir(parents=True, exist_ok=True)

    ######################
    # Become a Certificate Authority
    ######################

    c.run(f"openssl genrsa -out {folder / ca_name}.key 2048")
    c.run(
        f"openssl req -x509 -new -nodes -key {folder / ca_name}.key -sha256 -days 825 -out {folder / ca_name}.pem -subj '/C=US/ST=Denial/L=Springfield/O=Dis/CN={domain_name}'"
    )

    ######################
    # Create CA-signed certs
    ######################

    c.run(f"openssl genrsa -out {folder / domain_name}.key 2048")
    c.run(
        f"openssl req -new -key {folder / domain_name}.key -out {folder / domain_name}.csr -subj '/C=US/ST=Denial/L=Springfield/O=Dis/CN={domain_name}'"
    )

    with open(f"{folder / domain_name}.ext", "w") as f:
        f.write("authorityKeyIdentifier=keyid,issuer\n")
        f.write("basicConstraints=CA:FALSE\n")
        f.write(
            "keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment\n"
        )
        f.write("subjectAltName = @alt_names\n")
        f.write("[alt_names]\n")
        f.write(f"DNS.1 = {domain_name}\n")

    c.run(
        f"openssl x509 -req -in {folder / domain_name}.csr -CA {folder / ca_name}.pem -CAkey {folder / ca_name}.key -CAcreateserial -out {folder / domain_name}.crt -days 825 -sha256 -extfile {folder / domain_name}.ext"
    )

    cert_path = folder / f"{domain_name}.crt"
    key_path = folder / f"{domain_name}.key"

    return cert_path, key_path


@task(name="init")
def generate_env(c, hostname="predykt.dev"):
    cert_path, key_path = generate_cert(c, Path(".local"), hostname)

    with open(cert_path, "rb") as key_file:
        key = key_file.read()
        key_base64 = base64.b64encode(key).decode("ascii")

    with open(key_path, "rb") as key_file:
        private_key = key_file.read()
        private_key_base64 = base64.b64encode(private_key).decode("ascii")

    with open(".env", "w") as f:
        f.write("POSTGRES_USERNAME=predyktuser\n")
        f.write("POSTGRES_PASSWORD=predyktpassword\n")
        f.write("POSTGRES_HOST=127.0.0.1\n")
        f.write("POSTGRES_DB=predykt\n")
        f.write(f"JWT_PUBLIC_KEY={key_base64}\n")
        f.write(f"JWT_PRIVATE_KEY={private_key_base64}\n")
        f.write(f"HOSTNAME={hostname}\n")


@task(name="upload-base-project")
def upload_base_project(c):
    cwd = os.getcwd()
    truncate_db(c)
    c.run(
        f"curl -X POST -F 'file=@{cwd}/project-setup.jsonl'  http://localhost:8000/api/import"
    )


@task(name="upload-project")
def upload_project(c):
    cwd = os.getcwd()
    c.run(
        f"curl -X POST -F 'file=@{cwd}/project.jsonl'  http://localhost:8000/api/import"
    )

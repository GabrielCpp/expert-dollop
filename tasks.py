from os import environ, path, getcwd
from typing import Optional, List
from dotenv import load_dotenv
from invoke import task
from pathlib import Path
from uuid import uuid4
from urllib.parse import urlparse, urlunparse, urlsplit, urlunsplit
import base64
import asyncio

from expert_dollup.shared.starlette_injection import *
from expert_dollup.shared.database_services import *
from expert_dollup.core.domains import *
from expert_dollup.app.modules import (
    build_container,
    expert_dollup_metadatas,
    auth_metadatas,
)


load_dotenv()


async def truncate_db(db_url_name: str, metadatas: List[RepositoryMetadata]):
    connection = create_connection(environ[db_url_name])
    connection.load_metadatas(metadatas)
    await connection.truncate_db()


async def get_token(oauth: Optional[str] = None):
    oauth = SuperUser.oauth_id if oauth is None else oauth
    container = build_container()
    auth_service: AuthService = container.get(AuthService)
    token = auth_service.make_token(oauth)
    return token


async def get_random_empty_token():
    container = build_container()
    auth_service: AuthService = container.get(AuthService)
    token = auth_service.make_token(str(uuid4()))
    return token


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


def generate_jwt_key_pair(c, folder: Path, name: str):
    folder.mkdir(parents=True, exist_ok=True)
    c.run(f"openssl genrsa -out {folder / name}-private.pem 2048")
    c.run(
        f"openssl rsa -in {folder / name}-private.pem -pubout > {folder / name}-public.pem"
    )

    private_path = folder / f"{name}-private.pem"
    public_path = folder / f"{name}-public.pem"

    return public_path, private_path


async def create_loal_db_users(url):
    db_kind = resolve_scheme(urlparse(url).scheme)

    if db_kind != "mongodb":
        return

    from motor.motor_asyncio import AsyncIOMotorClient

    u = urlsplit(url)
    db_name = u.path.strip(" /")
    client = AsyncIOMotorClient(
        str(urlunsplit((u.scheme, u.netloc, "admin", u.query, u.fragment)))
    )
    db = client.get_database(db_name)

    await db.command(
        "createUser",
        u.username,
        pwd=u.password,
        roles=["readWrite", "dbAdmin", "dbOwner"],
    )


def apply_db_migrations(c, url):
    db_kind = resolve_scheme(url.scheme)
    migration_folder = Path("migrations") / db_kind / url.path[1:]

    if db_kind == "mongodb":
        environ["DB_URL"] = urlunparse(url)
        c.run(f"python {migration_folder}")
    elif db_kind == "postgres":
        c.run("alembic upgrade head")


def resolve_scheme(scheme):
    if scheme.startswith("mongodb"):
        return "mongodb"

    return scheme


@task(name="start-https")
def start_https(c):
    c.run(
        "uvicorn expert_dollup.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile .local/predykt.dev.key --ssl-certfile .local/predykt.dev.crt"
    )


@task
def start(c):
    c.run("uvicorn expert_dollup.main:app --reload --host 0.0.0.0 --port 8000")


@task(name="start:docker")
def start_docker(c):
    c.run(
        "docker build --target=release -t expert-dollup-release . && docker run --env-file .env -it --entrypoint /bin/bash   "
    )


@task(name="test:docker")
def test_docker(c):
    c.run(
        "docker build --target=test -t expert-dollup-test . && docker run expert-dollup-test"
    )


@task
def test(c, k=None, p=None, x=False, s=None):
    x = "-x" if x else ""
    s = "--random-order-seed={s}" if s else ""
    if k:
        c.run(f"pytest {x} -k {k} --random-order {s}")
    elif p:
        c.run(f"pytest {p} {x} --random-order {s}")
    else:
        c.run(f"pytest {x} --random-order {s}")


@task(name="env:init")
def generate_env(
    c,
    hostname="127.0.0.1",
    auth_db="mongodb",
    expert_dollup_db="mongodb",
    local_files=".local",
    username="predyktuser",
    password="predyktpassword",
):
    if path.exists(".env"):
        print("Environement file already exists")

    public_path, private_path = generate_jwt_key_pair(c, Path(local_files), "jwt")

    with open(public_path, "rb") as key_file:
        key = key_file.read()
        key_base64 = base64.b64encode(key).decode("ascii")

    with open(private_path, "rb") as key_file:
        private_key = key_file.read()
        private_key_base64 = base64.b64encode(private_key).decode("ascii")

    crendetial_part = (
        "" if username == "" or password == "" else f"{username}:{password}@"
    )

    configs_lines = [
        f"EXPERT_DOLLUP_DB_URL={expert_dollup_db}://{crendetial_part}{hostname}:27017/expert_dollup",
        f"AUTH_DB_URL={auth_db}://{crendetial_part}{hostname}:27017/auth",
        f"JWT_PUBLIC_KEY={key_base64}",
        f"JWT_PRIVATE_KEY={private_key_base64}",
        "FASTAPI_ENV=development",
        "PORT=8000",
        'JWT_AUDIENCES=["https://dev-id3ta63u.us.auth0.com/api/v2/","https://dev-id3ta63u.us.auth0.com/userinfo"]',
        "JWT_ISSUER=https://dev-id3ta63u.us.auth0.com/",
        "APP_BUCKET_NAME=expertdollup",
        f"DB_USERNAME={username}",
        f"DB_PASSWORD={password}",
    ]

    with open(".env", "w") as f:
        for configs_line in configs_lines:
            f.write(f"{configs_line}\n")


@task(name="env:reset")
def resetEnv(c, force=False):
    load_dotenv()

    if force:
        c.run("docker system prune -a -f")
        c.run("docker stop $(docker ps -a -q)")
        c.run("docker rm $(docker ps -a -q)")
        c.run("docker rmi $(docker images -a -q)")
        c.run("docker volume prune -f")

    expert_dollup_db_url = urlparse(environ["EXPERT_DOLLUP_DB_URL"])
    auth_db_url = urlparse(environ["AUTH_DB_URL"])

    images_to_load = set()
    images_to_load.add(expert_dollup_db_url.scheme)
    images_to_load.add(auth_db_url.scheme)

    commands = []

    for file_suffix in images_to_load:
        commands.append(
            f"docker-compose -f images/docker-compose.{file_suffix}.yml down --remove-orphans --volumes"
        )
        commands.append(
            f"docker-compose -f images/docker-compose.{file_suffix}.yml  up --detach --force-recreate"
        )

    print(commands)
    c.run(" && ".join(commands))

    print("Creating local db users")
    asyncio.run(create_loal_db_users(environ["EXPERT_DOLLUP_DB_URL"]))
    asyncio.run(create_loal_db_users(environ["AUTH_DB_URL"]))

    print("applying local db migrations")
    apply_db_migrations(c, expert_dollup_db_url)
    apply_db_migrations(c, auth_db_url)


@task(name="migration:apply")
def migration_apply(c):
    c.run(
        "docker build --target=migration -t expert-dollup-migration . && docker run --env-file .env --env EXPERT_DOLLUP_DB_URL=$EXPERT_DOLLUP_DB_URL --env AUTH_DB_URL=$AUTH_DB_URL expert-dollup-migration"
    )


@task(name="db:migrate")
def migrate_db(c, url=None):
    if url is None:
        expert_dollup_db_url = urlparse(environ["EXPERT_DOLLUP_DB_URL"])
        auth_db_url = urlparse(environ["AUTH_DB_URL"])

        apply_db_migrations(c, expert_dollup_db_url)
        apply_db_migrations(c, auth_db_url)
    else:
        apply_db_migrations(c, urlparse(url))


@task(name="db:migration:new")
def newMigration(c, message=None):
    if message is None:
        print("Message required")
        return

    c.run(f'alembic revision -m "{message}"')


@task(name="db:truncate")
def db_truncate(c):
    asyncio.run(truncate_db("EXPERT_DOLLUP_DB_URL", expert_dollup_metadatas))
    asyncio.run(truncate_db("AUTH_DB_URL", auth_metadatas))


@task(name="upload-base-project")
def upload_base_project(c, token=None, userid=None, hostname=None):
    cwd = getcwd()

    if hostname is None:
        asyncio.run(truncate_db("EXPERT_DOLLUP_DB_URL", expert_dollup_metadatas))
        hostname = "http://localhost:8000"

    if token is None:
        asyncio.run(
            truncate_db(
                "AUTH_DB_URL",
                [
                    m
                    for m in auth_metadatas
                    if m.domain is User or m.domain is Organization
                ],
            )
        )
        load_default_users(c)
        token = asyncio.run(get_token())

    if userid is None:
        userid = "5d9c68c6-c50e-d3d0-2a2f-cf54f63993b6"

    c.run(
        f"curl -X POST -H 'Authorization: Bearer {token}' -H \"Content-Type: multipart/form-data\" -F 'file=@{cwd}/project-setup.jsonl' -F user_id={userid} {hostname}/api/ressources/imports"
    )


@task(name="upload-project")
def upload_project(c, token=None, userid=None, hostname=None):
    cwd = getcwd()

    if hostname is None:
        hostname = "http://localhost:8000"

    if token is None:
        token = asyncio.run(get_token())

        c.run(
            f"curl -X DELETE -H 'Authorization: Bearer {token}'  {hostname}/api/projects/11ec4bbb-ebe8-fa7c-bcc3-42010a800002"
        )

    if userid is None:
        userid = "5d9c68c6-c50e-d3d0-2a2f-cf54f63993b6"

    c.run(
        f"curl -X POST -H 'Authorization: Bearer {token}' -H \"Content-Type: multipart/form-data\" -F 'file=@{cwd}/project.jsonl' -F user_id={userid} {hostname}/api/ressources/imports"
    )


@task(name="refresh-cache")
def refreshcache(c):
    cwd = getcwd()
    c.run(
        f"curl -X POST -F 'file=@{cwd}/project.jsonl' http://localhost:8000/api/report_definition/8e084b1e-b331-4644-8485-5e91e21770b2/refresh_cache"
    )


@task(name="testreport")
def testreport(c):
    c.run(
        "curl http://localhost:8000/api/projects/11ec4bbb-ebe8-fa7c-bcc3-42010a800002/report/8e084b1e-b331-4644-8485-5e91e21770b2/minimal"
    )


@task(name="token")
def make_token(c, oauth=None):
    print(asyncio.run(get_token(oauth)))


@task(name="random-token")
def make_random_token(c):
    print(asyncio.run(get_random_empty_token()))


@task(name="load-default-users")
def load_default_users(c):
    from expert_dollup.infra.ressource_auth_db import RessourceAuthDatabase
    from tests.fixtures import FakeDb

    async def reload_db():
        container = build_container()
        user_db = container.get(RessourceAuthDatabase)
        database_context = container.get(DatabaseContext)
        db = FakeDb.create_from([SuperUser()])

        await user_db.truncate_db()
        await database_context.upserts(Organization, db.all(Organization))
        await database_context.upserts(User, db.all(User))

    asyncio.run(reload_db())

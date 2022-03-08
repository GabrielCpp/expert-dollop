from dotenv import load_dotenv
from invoke import task
from pathlib import Path
from urllib.parse import urlparse, urlunparse
from os import environ, path, getcwd
import base64
import asyncio


async def truncate_db(db_url_name: str, tables=None):
    from expert_dollup.shared.database_services import create_connection
    import expert_dollup.infra.expert_dollup_db as daos

    load_dotenv()
    connection = create_connection(environ[db_url_name], daos)
    await connection.truncate_db(tables)


async def get_token(oauth: str):
    from dotenv import load_dotenv
    from expert_dollup.app.modules import build_container
    from expert_dollup.shared.starlette_injection import AuthService

    load_dotenv()
    container = build_container()
    auth_service: AuthService = container.get(AuthService)
    token = auth_service.make_token(oauth)
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


def apply_db_migrations(c, url):
    db_kind = resolve_scheme(url.scheme)
    migration_folder = Path("migrations") / db_kind / url.path[1:]

    if db_kind == "mongodb":
        environ["DB_URL"] = urlunparse(url)
        c.run(f"poetry run python {migration_folder}")
    elif db_kind == "postgres":
        c.run("poetry run alembic upgrade head")


def resolve_scheme(scheme):
    return scheme


@task(name="start-https")
def start_https(c):
    c.run(
        "poetry run uvicorn expert_dollup.main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile .local/predykt.dev.key --ssl-certfile .local/predykt.dev.crt"
    )


@task
def start(c):
    c.run(
        "poetry run uvicorn expert_dollup.main:app --reload --host 0.0.0.0 --port 8000"
    )


@task(name="env:init")
def generate_env(
    c,
    hostname="127.0.0.1",
    auth_db="mongodb",
    expert_dollup_db="mongodb",
    local_files=".local",
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

    configs_lines = [
        f"EXPERT_DOLLUP_DB_URL={expert_dollup_db}://predyktuser:predyktpassword@{hostname}:27017/expert_dollup",
        f"AUTH_DB_URL={auth_db}://predyktuser:predyktpassword@{hostname}:27017/auth",
        f"JWT_PUBLIC_KEY={key_base64}",
        f"JWT_PRIVATE_KEY={private_key_base64}",
        f"HOSTNAME={hostname}",
        "FASTAPI_ENV=development",
        "DB_USERNAME=predyktuser",
        "DB_PASSWORD=predyktpassword",
    ]

    with open(".env", "w") as f:
        for configs_line in configs_lines:
            f.write(f"{configs_line}\n")


@task(name="env:reset")
def resetEnv(c):
    load_dotenv()

    expert_dollup_db_url = urlparse(environ["EXPERT_DOLLUP_DB_URL"])
    auth_db_url = urlparse(environ["AUTH_DB_URL"])

    images_to_load = set()
    images_to_load.add(expert_dollup_db_url.scheme)
    images_to_load.add(auth_db_url.scheme)

    commands = []

    for file_suffix in images_to_load:
        commands.append(
            f"docker-compose -f docker-compose.{file_suffix}.yml down --remove-orphans --volumes"
        )
        commands.append(
            f"docker-compose -f docker-compose.{file_suffix}.yml  up --detach --force-recreate"
        )

    print(commands)
    c.run(" && ".join(commands))

    apply_db_migrations(c, expert_dollup_db_url)
    apply_db_migrations(c, auth_db_url)


@task
def black(c):
    c.run("poetry run black .")


@task(name="db:migrate")
def migrate_db(c, url):
    apply_db_migrations(c, urlparse(url))


@task(name="db:migration:new")
def newMigration(c, message=None):
    if message is None:
        print("Message required")
        return

    c.run('poetry run alembic revision -m "{}"'.format(message))


@task(name="db:truncate")
def db_truncate(c):
    asyncio.run(truncate_db("EXPERT_DOLLUP_DB_URL"))
    asyncio.run(truncate_db("AUTH_DB_URL"))


@task(name="upload-base-project")
def upload_base_project(c):
    cwd = getcwd()
    db_truncate(c, poetry=True)
    load_default_users(c)
    token = asyncio.run(get_token("testuser"))
    c.run(
        f"curl -X POST -H 'Authorization: Bearer {token}' -F 'file=@{cwd}/project-setup.jsonl' http://localhost:8000/api/import/5d9c68c6-c50e-d3d0-2a2f-cf54f63993b6"
    )


@task(name="upload-project")
def upload_project(c):
    cwd = getcwd()
    token = asyncio.run(get_token("testuser"))
    c.run(
        f"curl -X DELETE -H 'Authorization: Bearer {token}'  http://localhost:8000/api/project/11ec4bbb-ebe8-fa7c-bcc3-42010a800002"
    )
    c.run(
        f"curl -X POST -H 'Authorization: Bearer {token}' -F 'file=@{cwd}/project.jsonl' http://localhost:8000/api/import/5d9c68c6-c50e-d3d0-2a2f-cf54f63993b6"
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
        "curl http://localhost:8000/api/project/11ec4bbb-ebe8-fa7c-bcc3-42010a800002/report/8e084b1e-b331-4644-8485-5e91e21770b2/minimal"
    )


@task(name="token")
def make_token(c, oauth="testuser"):
    print(asyncio.run(get_token("testuser")))


@task(name="load-default-users")
def load_default_users(c):
    from dotenv import load_dotenv
    from expert_dollup.app.modules import build_container
    from expert_dollup.core.domains import User
    from expert_dollup.shared.database_services import CollectionService
    from expert_dollup.infra.ressource_auth_db import RessourceAuthDatabase
    from tests.fixtures.seeds import make_default_users

    async def reload_db():
        load_dotenv()
        container = build_container()
        user_db = container.get(RessourceAuthDatabase)
        user_service = container.get(CollectionService[User])

        await user_db.truncate_db()
        await user_service.insert_many(make_default_users())

    asyncio.run(reload_db())

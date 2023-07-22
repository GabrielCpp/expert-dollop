from os import environ
import base64
from pydantic import BaseModel
from typing import Optional, List, Callable
from json import loads


class JwtSettings(BaseModel):
    issuer: str
    audiences: List[str]
    public_key: str
    private_key: Optional[str]


class AppSettings(BaseModel):
    authjwt: JwtSettings


def decode_base64(value: str) -> str:
    return base64.decodebytes(value.encode("ascii")).decode("ascii")


def get_config(
    name,
    decoder: Callable[[str], str] = str,
    default: Optional[str] = None,
    required=True,
) -> str:
    value = environ.get(name, default)

    if value is None:
        if required:
            raise Exception(f"Missing configuration '{name}'")

        return None

    return decoder(environ[name])


def load_app_settings() -> AppSettings:
    authjwt_public_key = base64.decodebytes(
        environ.get("JWT_PUBLIC_KEY").encode("ascii")
    ).decode("ascii")

    if "JWT_PRIVATE_KEY" in environ:
        JWT_PRIVATE_KEY = environ["JWT_PRIVATE_KEY"].encode("ascii")
        authjwt_private_key = base64.decodebytes(JWT_PRIVATE_KEY).decode("ascii")
    else:
        authjwt_private_key = None

    return AppSettings(
        authjwt=JwtSettings(
            issuer=get_config("JWT_ISSUER"),
            audiences=get_config("JWT_AUDIENCES", loads),
            public_key=get_config("JWT_PUBLIC_KEY", decode_base64),
            private_key=get_config("JWT_PRIVATE_KEY", decode_base64, required=False),
        )
    )

from os import environ
import base64
from pydantic import BaseModel
from typing import Optional


class AppSettings(BaseModel):
    authjwt_algorithm: str = "RS256"
    authjwt_decode_audience = "https://dev-id3ta63u.us.auth0.com/api/v2/"
    authjwt_public_key: str
    authjwt_private_key: Optional[str]


def load_app_settings():
    authjwt_public_key = base64.decodebytes(
        environ.get("JWT_PUBLIC_KEY").encode("ascii")
    ).decode("ascii")

    if "JWT_PRIVATE_KEY" in environ:
        JWT_PRIVATE_KEY = environ["JWT_PRIVATE_KEY"].encode("ascii")
        authjwt_private_key = base64.decodebytes(JWT_PRIVATE_KEY).decode("ascii")
    else:
        authjwt_private_key = None

    return AppSettings(
        authjwt_public_key=authjwt_public_key, authjwt_private_key=authjwt_private_key
    )

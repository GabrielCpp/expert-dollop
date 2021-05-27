import os
import base64
from pydantic import BaseModel


class AppSettings(BaseModel):
    authjwt_algorithm: str = "RS256"
    authjwt_decode_audience = "https://dev-id3ta63u.us.auth0.com/api/v2/"
    authjwt_public_key: str
    authjwt_private_key: str


def load_app_settings():
    authjwt_public_key = base64.decodebytes(
        os.environ.get("JWT_PUBLIC_KEY").encode("ascii")
    ).decode("ascii")
    authjwt_private_key = base64.decodebytes(
        os.environ.get("JWT_PRIVATE_KEY").encode("ascii")
    ).decode("ascii")

    return AppSettings(
        authjwt_public_key=authjwt_public_key, authjwt_private_key=authjwt_private_key
    )
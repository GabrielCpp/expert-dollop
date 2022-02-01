from os import environ


def is_development():
    return environ.get("FASTAPI_ENV", "production") == "development"

from os import environ
from starlette.config import Config


config = Config("development.env")


PROJECT_TITLE = config("PROJECT_TITLE", str, "")
SITE_PORT = config("SITE_PORT", int)
SITE_HOST = config("SITE_HOST", str)

_POSTGRES_DB = config("POSTGRES_DB")
_POSTGRES_USER = config("POSTGRES_USER")
_POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")

DATABASE_URL = f"postgresql://{_POSTGRES_USER}:{_POSTGRES_PASSWORD}@db:5432/{_POSTGRES_DB}"

environ["DATABASE_URL"] = DATABASE_URL



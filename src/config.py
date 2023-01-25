from os import environ
from starlette.config import Config


config = Config("development.env")


PROJECT_TITLE = config("PROJECT_TITLE", str, "")
SITE_PORT = config("SITE_PORT", int)
SITE_HOST = config("SITE_HOST", str)

POSTGRES_DB = config("POSTGRES_DB")
POSTGRES_USER = config("POSTGRES_USER")
POSTGRES_PASSWORD = config("POSTGRES_PASSWORD")
POSTGRES_HOST = "db"
POSTGRES_PORT = "5432"

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

environ["DATABASE_URL"] = DATABASE_URL

JWT_EXPIRE_MINUTES = config("JWT_EXPIRE_MINUTES", int, 60)
SECRET_KEY = config("SECRET_KEY")
ALGORITHM = config("ALGORITHM")

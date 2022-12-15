from sqlalchemy import Column, Integer, String, Table

from .base import metadata


users = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("login", String(63), unique=True),
    Column("password", String(31)),
)

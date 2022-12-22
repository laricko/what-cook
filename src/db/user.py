from sqlalchemy import Column, Integer, String, Table

from db.base import metadata


users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(63), unique=True),
    Column("password", String(63)),
)

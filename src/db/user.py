from sqlalchemy import Column, Integer, String, Table, Boolean, ForeignKey

from db.base import metadata


user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("email", String(63), unique=True, nullable=False),
    Column("password", String(63), nullable=False),
    Column("verified", Boolean, server_default="f", nullable=False),
)

token = Table(
    "token",
    metadata,
    Column(
        "user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    ),
    Column("value", String(63), unique=True, nullable=False),
)

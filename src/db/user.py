from sqlalchemy import Column, Integer, String, Table, Boolean, ForeignKey

from db.base import metadata


user = Table(
    "user",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("first_name", String(31)),
    Column("last_name", String(31)),
    Column("email", String(63), unique=True, nullable=False, index=True),
    Column("phone_number", String(15)),
    Column("password", String(63), nullable=False),
    Column("verified", Boolean, server_default="f", nullable=False),
    # Dinner host data
    Column("can_be_dinner_host", Boolean, server_default="f", nullable=False),
    Column("address", String(127)),
    # Admin
    Column("is_staff", Boolean, server_default="f", nullable=False),
)

token = Table(
    "token",
    metadata,
    Column(
        "user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    ),
    Column("value", String(63), unique=True, nullable=False),
)

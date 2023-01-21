from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    SmallInteger,
    UniqueConstraint,
)

from db.base import metadata


ingredient = Table(
    "ingredient",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(31), unique=True),
)

kitchen_ingredient = Table(
    "kitchen_ingredient",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "ingredient_id",
        Integer,
        ForeignKey("ingredient.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "user_id", Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False
    ),
    Column("weight", Integer),  # Use constraint ck_kitchen_ingredient_weight_positive
    Column(
        "count", SmallInteger
    ),  # Use constraint ck_kitchen_ingredient_count_positive
    UniqueConstraint("user_id", "ingredient_id", name="uix_1"),
)

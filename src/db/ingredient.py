from sqlalchemy import Column, Integer, String, ForeignKey, Table

from .base import metadata


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
    Column("ingredient_id", Integer, ForeignKey("ingredient.id")),
)

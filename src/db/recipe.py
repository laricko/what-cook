from sqlalchemy import Table, ForeignKey, String, SmallInteger, Column, Integer, Boolean

from db.base import metadata


recipe = Table(
    "recipe",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("title", String(255), unique=True, nullable=False),
    Column("description", String(255), nullable=False),
    Column("public", Boolean, server_default="f", nullable=False),
    Column("author_id", ForeignKey("user.id", ondelete="CASCADE"), nullable=False),
)

step = Table(
    "step",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("description", String(255), nullable=False),
    Column("order", SmallInteger, nullable=False),  # ck_step_order_positive
    Column("recipe_id", ForeignKey("recipe.id", ondelete="CASCADE"), nullable=False),
)

recipe_ingredient = Table(
    "recipe_ingredient",
    metadata,
    Column("id", Integer, primary_key=True),
    Column(
        "ingredient_id",
        Integer,
        ForeignKey("ingredient.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column(
        "recipe_id",
        Integer,
        ForeignKey("recipe.id", ondelete="CASCADE"),
        nullable=False,
    ),
    Column("weight", Integer),  # ck_recipe_ingredient_weight_positive
    Column("count", SmallInteger),  # ck_recipe_ingredient_count_positive
)

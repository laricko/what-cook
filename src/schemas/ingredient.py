from typing import Optional

from pydantic import BaseModel, root_validator


class Ingredient(BaseModel):
    id: int
    title: str


class KitchenIngredient(BaseModel):
    id: int
    ingredient: Ingredient
    weight: Optional[int]
    count: Optional[int]

    @root_validator(pre=True)
    def parse_flat_ingredient_data(cls, values):
        values["ingredient"] = Ingredient(
            id=values.get("id_1"), title=values.get("title")
        )
        return values

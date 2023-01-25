from typing import Optional

from pydantic import BaseModel


class Ingredient(BaseModel):
    id: int
    title: str


class KitchenIngredient(BaseModel):
    id: int
    ingredient: Ingredient
    weight: Optional[int]
    count: Optional[int]

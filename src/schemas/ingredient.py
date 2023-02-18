from pydantic import BaseModel


class Ingredient(BaseModel):
    id: int
    title: str


class KitchenIngredient(BaseModel):
    id: int
    ingredient: Ingredient
    weight: None | int
    count: None | int

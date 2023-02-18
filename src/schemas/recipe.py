from pydantic import BaseModel

from schemas.ingredient import Ingredient


class Step(BaseModel):
    id: int
    description: str
    order: int


class RecipeIngredient(BaseModel):
    ingredient: Ingredient
    weight: None | int
    count: None | int


class Recipe(BaseModel):
    id: int
    title: str
    description: str
    public: bool
    steps: list[Step]
    recipe_ingredients: list[RecipeIngredient]

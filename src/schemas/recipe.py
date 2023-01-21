from typing import List, Optional

from pydantic import BaseModel, root_validator

from schemas.ingredient import Ingredient


class Step(BaseModel):
    id: int
    description: str
    order: int


class RecipeIngredient(BaseModel):
    ingredient: Ingredient
    weight: Optional[int]
    count: Optional[int]


class Recipe(BaseModel):
    id: int
    title: str
    description: str
    public: bool
    steps: List[Step]
    recipe_ingredients: List[RecipeIngredient]

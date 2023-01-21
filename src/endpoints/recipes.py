from asyncio import create_task
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, func
from pydantic import BaseModel, validator, parse_obj_as
from sqlalchemy.dialects.postgresql import aggregate_order_by

from auth_services import get_current_user_is_verified
from utils.get_fields_for_json_build_object import get_fields_for_json_build_object
from schemas.user import User
from schemas.recipe import Recipe
from db.base import database, engine, session
from db import recipe, step, recipe_ingredient, user as user_table, ingredient


recipes_router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
    dependencies=[Depends(get_current_user_is_verified)],
)


base_recipe_query = (
    select(
        [
            *recipe.columns,
            func.array_agg(
                func.jsonb_build_object(
                    *get_fields_for_json_build_object(step)
                ).distinct()
            ).label("steps"),
            func.array_agg(
                func.jsonb_build_object(
                    *get_fields_for_json_build_object(recipe_ingredient),
                    "ingredient",
                    func.jsonb_build_object(
                        *get_fields_for_json_build_object(ingredient)
                    ),
                ).distinct()
            ).label("recipe_ingredients"),
            func.jsonb_build_object(
                *get_fields_for_json_build_object(user_table)
            ).label("author"),
        ]
    )
    .select_from(
        recipe.join(step, recipe.c.id == step.c.recipe_id)
        .join(recipe_ingredient, recipe.c.id == recipe_ingredient.c.recipe_id)
        .join(user_table, recipe.c.author_id == user_table.c.id)
        .join(ingredient, ingredient.c.id == recipe_ingredient.c.ingredient_id)
    )
    .group_by(recipe.c.id, recipe.c.title, user_table.c.id)
)


@recipes_router.get("/my", response_model=List[Recipe])
async def my_recipes(user: User = Depends(get_current_user_is_verified)):
    query = base_recipe_query.where(recipe.c.author_id == user.id)
    recipes = session.execute(query).fetchall()
    return parse_obj_as(List[Recipe], recipes)


@recipes_router.get("/")
async def recipes(title: Optional[str] = None):
    filter = [recipe.c.title.ilike(f"%{title}%")] if title is not None else []
    query = base_recipe_query.where(*filter, recipe.c.public == True)
    recipes = session.execute(query).fetchall()
    return parse_obj_as(List[Recipe], recipes)


class AddIngredientsData(BaseModel):
    ingredient_id: int
    weight: Optional[int]
    count: Optional[int]

    @validator("weight", "count")
    def check_weight_and_count_positive(cls, v):
        if v is not None and v < 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "only positive fields")
        return v


class AddStepsData(BaseModel):
    description: str


class CreateRecipeData(BaseModel):
    title: str
    description: str
    ingredients: List[AddIngredientsData]
    steps: List[AddStepsData]

    @validator("title")
    def validate_title_is_unique(cls, v):
        query = select(recipe).where(recipe.c.title == v)
        with engine.connect() as con:
            rows = con.execute(query)
            recipe_obj = rows.fetchone()
            if recipe_obj:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST, "recipe already exists"
                )
        return v


@recipes_router.post("/")
async def create_recipe(
    data: CreateRecipeData, user: User = Depends(get_current_user_is_verified)
):
    query_to_create_recipe = insert(recipe).values(
        title=data.title, description=data.description, author_id=user.id
    )
    recipe_id = await create_task(database.execute(query_to_create_recipe))
    ingredients = [
        {**ingredient.dict(), "recipe_id": recipe_id} for ingredient in data.ingredients
    ]
    query_to_set_ingredients = insert(recipe_ingredient).values(ingredients)
    await create_task(database.execute(query_to_set_ingredients))
    steps = [
        {**step.dict(), "recipe_id": recipe_id, "order": num}
        for num, step in enumerate(data.steps, 1)
    ]
    query_to_set_steps = insert(step).values(steps)
    await create_task(database.execute(query_to_set_steps))
    return data

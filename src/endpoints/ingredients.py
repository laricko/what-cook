from typing import Optional, List
from asyncio import create_task

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, delete, update, and_
from pydantic import BaseModel, validator, parse_obj_as
from asyncpg.exceptions import ForeignKeyViolationError

from models.user import User
from models.ingredient import Ingredient, KitchenIngredient
from db import ingredient, kitchen_ingredient
from db.base import database
from auth_service import get_current_user_is_verified, get_current_user


ingredients_router = APIRouter(tags=["ingedients"])


@ingredients_router.get("/ingredients", response_model=List[Ingredient])
async def ingredients(
    user: User = Depends(get_current_user), title: Optional[str] = None
):
    filter = [ingredient.c.title.ilike(f"%{title}%")] if title is not None else []
    query = select(ingredient).where(*filter)
    ingredients = await database.fetch_all(query)
    return parse_obj_as(List[Ingredient], ingredients)


class AddToMyKitchenData(BaseModel):
    weight: Optional[int]
    count: Optional[int]

    @validator("weight", "count")
    def check_weight_and_count_positive(cls, v):
        if v is not None and v < 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "only positive fields")
        return v


@ingredients_router.post("/ingedients/{ingredient_id}/set-count-kitchen-ingredient")
async def set_count_kitchen_ingredient(
    ingredient_id: int,
    data: AddToMyKitchenData,
    user: User = Depends(get_current_user_is_verified),
):
    if data.weight in (None, 0) and data.count in (None, 0):
        query = delete(kitchen_ingredient).where(
            and_(
                kitchen_ingredient.c.user_id == user.id,
                kitchen_ingredient.c.ingredient_id == ingredient_id,
            )
        )
        await create_task(database.execute(query))
        return data
    inserting_data = dict(**data.dict(), user_id=user.id, ingredient_id=ingredient_id)
    query = (
        update(kitchen_ingredient)
        .where(
            and_(
                kitchen_ingredient.c.user_id == user.id,
                kitchen_ingredient.c.ingredient_id == ingredient_id,
            )
        )
        .values(**inserting_data)
        .returning(kitchen_ingredient.c.id)
    )
    result = await create_task(database.execute(query))
    if not result:
        query = insert(kitchen_ingredient).values(**inserting_data)
        try:
            await create_task(database.execute(query))
        except ForeignKeyViolationError:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "Ingredient with such id does not exists"
            )
    return data


@ingredients_router.get("/ingredients/my")
async def my_ingredients(user: User = Depends(get_current_user_is_verified)):
    query = (
        select(kitchen_ingredient, ingredient)
        .where(kitchen_ingredient.c.user_id == user.id)
        .join(
            ingredient,
            ingredient.c.id == kitchen_ingredient.c.ingredient_id,
            isouter=True,
        )
    )
    k_ingredients = await database.fetch_all(query)
    return parse_obj_as(List[KitchenIngredient], k_ingredients)


@ingredients_router.post("/ingredients/clear")
async def clear_my_ingredients(user: User = Depends(get_current_user_is_verified)):
    query = delete(kitchen_ingredient).where(kitchen_ingredient.c.user_id == user.id)
    return await database.execute(query)

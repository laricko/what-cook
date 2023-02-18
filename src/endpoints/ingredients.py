from asyncio import create_task

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, insert, delete, update, and_, func
from pydantic import BaseModel, validator

from schemas.user import User
from schemas.ingredient import Ingredient, KitchenIngredient
from db import ingredient, kitchen_ingredient
from db.base import database, session
from utils.auth_services import get_current_user_is_verified
from utils.get_fields_for_json_build_object import get_fields_for_json_build_object


ingredients_router = APIRouter(prefix="/ingredients", tags=["ingedients"])


@ingredients_router.get("/", response_model=list[Ingredient])
async def ingredients(title: None | str = None):
    filter = [ingredient.c.title.ilike(f"%{title}%")] if title is not None else []
    query = select(ingredient).where(*filter)
    return await database.fetch_all(query)


class SetCountKitchenIngredientData(BaseModel):
    weight: None | int
    count: None | int

    @validator("weight", "count")
    def check_weight_and_count_positive(cls, v):
        if v is not None and v < 0:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "only positive fields")
        return v


async def check_ingredient_exist(ingredient_id: int) -> int:
    query = select(ingredient.c.id).where(ingredient.c.id == ingredient_id)
    ing = await database.fetch_one(query)
    if not ing:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "Ingredient with such id does not exists"
        )
    return ingredient_id


@ingredients_router.post(
    "/{ingredient_id}/set-count-kitchen-ingredient",
    response_model=SetCountKitchenIngredientData,
)
async def set_count_kitchen_ingredient(
    data: SetCountKitchenIngredientData,
    ingredient_id: int = Depends(check_ingredient_exist),
    user: User = Depends(get_current_user_is_verified),
):
    # If weight = 0 or data = 0 we delete ingredient from user's kitchen
    if data.weight in (None, 0) and data.count in (None, 0):
        query_to_delete = delete(kitchen_ingredient).where(
            and_(
                kitchen_ingredient.c.user_id == user.id,
                kitchen_ingredient.c.ingredient_id == ingredient_id,
            )
        )
        await create_task(database.execute(query_to_delete))
        return data
    # else we update existing ingredient in user's kitchen. setting count or weight
    inserting_data = dict(**data.dict(), user_id=user.id, ingredient_id=ingredient_id)
    query_to_update = (
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
    # if nothing updated - we create ingredient in user's kitchen
    result = await database.execute(query_to_update)
    if not result:
        query_to_create = insert(kitchen_ingredient).values(**inserting_data)
        await create_task(database.execute(query_to_create))
    return data


@ingredients_router.get("/my", response_model=list[KitchenIngredient])
async def my_ingredients(user: User = Depends(get_current_user_is_verified)):
    query = (
        select(
            kitchen_ingredient,
            func.jsonb_build_object(
                *get_fields_for_json_build_object(ingredient)
            ).label("ingredient"),
        )
        .where(kitchen_ingredient.c.user_id == user.id)
        .join(
            ingredient,
            ingredient.c.id == kitchen_ingredient.c.ingredient_id,
            isouter=True,
        )
    )
    return session.execute(query).fetchall()


@ingredients_router.post("/clear")
async def clear_my_ingredients(user: User = Depends(get_current_user_is_verified)):
    query = delete(kitchen_ingredient).where(kitchen_ingredient.c.user_id == user.id)
    await create_task(database.execute(query))
    return {"detail": "success"}

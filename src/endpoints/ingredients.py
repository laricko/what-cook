from typing import Optional

from fastapi import APIRouter
from sqlalchemy import select

from db import ingredient
from db.base import database


router = APIRouter()


@router.get("/ingredients")
async def my_ingredient(title: Optional[str] = None):
    filter = [ingredient.c.title.ilike(f"%{title}%")] if title is not None else []
    query = select(ingredient).where(*filter)
    return await database.fetch_all(query)

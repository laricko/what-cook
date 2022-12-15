from fastapi import APIRouter

from db.base import database
from endpoints.ingredients import router


api_router = APIRouter(prefix="/api")
api_router.include_router(router)


@api_router.on_event("startup")
async def startup():
    await database.connect()

@api_router.on_event("shutdown")
async def shutdown():
    await database.disconnect()


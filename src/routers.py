from fastapi import APIRouter

from db.base import database
from endpoints.ingredients import router as ingredients_router
from endpoints.user import auth_router, user_router


api_router = APIRouter(prefix="/api")
api_router.include_router(ingredients_router)
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(user_router)


@api_router.on_event("startup")
async def startup():
    await database.connect()

@api_router.on_event("shutdown")
async def shutdown():
    await database.disconnect()


from fastapi import APIRouter

from db.base import database, session
from endpoints.ingredients import ingredients_router
from endpoints.auth import auth_router, verification_router
from endpoints.recipes import recipes_router


api_router = APIRouter(prefix="/api")
api_router.include_router(ingredients_router)
api_router.include_router(auth_router)
api_router.include_router(verification_router)
api_router.include_router(recipes_router)


@api_router.on_event("startup")
async def startup():
    await database.connect()


@api_router.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    session.close()

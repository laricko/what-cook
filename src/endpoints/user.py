from asyncio import create_task

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, validator, EmailStr
from sqlalchemy import insert, select

from db.base import database, engine
from db.user import users
from auth_service import (
    hash_password,
    verify_passwrod,
    create_access_token,
    get_current_user,
    JWTBearer,
)
from models.user import User


auth_router = APIRouter()


class RegisterData(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @validator("email")
    def check_email_not_exist(cls, v):
        query = select(users).where(users.c.email == v)
        with engine.connect() as con:
            rows = con.execute(query)
            user = rows.fetchone()
            if user:
                raise HTTPException(status.HTTP_400_BAD_REQUEST, "email already exists")
        return v

    @validator("confirm_password")
    def passwords_match(cls, v, values, **kwargs):
        if v != values["password"]:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "passwords do not match")
        return v


class LoginData(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(User):
    token: str


@auth_router.post("/register")
async def register(data: RegisterData):
    data_as_dict = data.dict()
    data_as_dict.pop("confirm_password")
    data_as_dict["password"] = hash_password(data.password)
    query = insert(users).values(**data_as_dict)
    await create_task(database.execute(query))
    return data_as_dict


@auth_router.post("/login")
async def login(data: LoginData):
    exc = HTTPException(
        status.HTTP_403_FORBIDDEN, "There is no user with such email and password"
    )
    query = select(users).where(users.c.email == data.email)
    user = await database.fetch_one(query)
    if not user:
        raise exc
    password_match = verify_passwrod(data.password, user.password)
    if not password_match:
        raise exc
    user_as_dict = dict(user._mapping)
    user_as_dict["token"] = create_access_token({"sub": data.email})
    return UserLoginResponse.parse_obj(user_as_dict)


user_router = APIRouter()


@user_router.get("/self-user")
async def self_user(user: str = Depends(get_current_user)):
    return user

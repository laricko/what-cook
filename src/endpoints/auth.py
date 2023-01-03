from asyncio import create_task
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, validator, EmailStr
from sqlalchemy import insert, select, update

from db.base import database, engine
from db.user import user as user_db, token as token_db
from auth_service import hash_password, verify_passwrod, create_access_token
from models.user import User, UserLoginResponse
from utils.send_mail import send_email


auth_router = APIRouter(tags=["auth"])


class RegisterData(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @validator("email")
    def check_email_not_exist(cls, v):
        query = select(user_db).where(user_db.c.email == v)
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


@auth_router.post("/register")
async def register(data: RegisterData):
    data_as_dict = data.dict()
    data_as_dict.pop("confirm_password")
    data_as_dict["password"] = hash_password(data.password)
    query = insert(user_db).values(**data_as_dict)
    user_id = await create_task(database.execute(query))
    random_token = str(uuid4())
    query = insert(token_db).values(user_id=user_id, value=random_token)
    await create_task(database.execute(query))
    url = f"http://localhost:8000/api/verify-email?token={random_token}"
    await create_task(send_email("Подтверждение", data.email, url))
    data_as_dict.pop("password")
    return data_as_dict


@auth_router.post("/login")
async def login(data: LoginData):
    exc = HTTPException(
        status.HTTP_403_FORBIDDEN, "There is no user with such email and password"
    )
    query = select(user_db).where(user_db.c.email == data.email)
    user = await database.fetch_one(query)
    if not user:
        raise exc
    password_match = verify_passwrod(data.password, user.password)
    if not password_match:
        raise exc
    user_as_dict = dict(user._mapping)
    user_as_dict["token"] = create_access_token({"sub": data.email})
    return UserLoginResponse.parse_obj(user_as_dict)


verification_router = APIRouter(tags=["verification"])


@verification_router.get("/verify-email")
async def verify_email(token: str):
    query = select(token_db).where(token_db.c.value == token)
    token_instance = await database.fetch_one(query)
    query = (
        update(user_db)
        .where(user_db.c.id == token_instance.user_id)
        .values(verified=True)
    )
    user = await database.execute(query)
    return user

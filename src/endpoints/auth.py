from asyncio import create_task

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, validator, EmailStr
from sqlalchemy import insert, select, update

from db.base import database, session
from db.user import user as user_db, token as token_db
from utils.auth_services import hash_password, verify_passwrod, create_access_token
from schemas.user import UserLoginResponse
from utils.send_email_verification import send_email_verification


auth_router = APIRouter(prefix="/auth", tags=["auth"])


class RegisterData(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str

    @validator("email")
    def check_email_not_exist(cls, v):
        email = session.query(user_db.c.email).filter_by(email=v).first()
        if email:
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
    query = insert(user_db).values(
        email=data.email, password=hash_password(data.password)
    )
    user_id = await database.execute(query)
    await create_task(send_email_verification(user_id, data.email))
    return data


@auth_router.post("/login", response_model=UserLoginResponse)
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
    query_to_get_token = select(token_db).where(token_db.c.value == token)
    token_instance = await database.fetch_one(query_to_get_token)
    if not token_instance:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "token not valid")
    query_to_get_user = select(user_db).where(user_db.c.id == token_instance.user_id)
    user = await database.fetch_one(query_to_get_user)
    if user.verified:
        return {"detail": "success"}
    query_to_make_user_verified = (
        update(user_db)
        .where(user_db.c.id == token_instance.user_id)
        .values(verified=True)
    )
    await database.execute(query_to_make_user_verified)
    return {"detail": "success"}

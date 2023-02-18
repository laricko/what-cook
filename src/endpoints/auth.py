from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, validator, EmailStr
from sqlalchemy import insert, select, update

from db.base import database, session
from db.user import user as user_db, token as token_db
from utils.auth_services import hash_password, verify_passwrod, create_access_token
from schemas.user import UserLoginResponse
from utils.send_mail import send_email


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
    data_as_dict = data.dict()
    data_as_dict.pop("confirm_password")
    data_as_dict["password"] = hash_password(data.password)
    query = insert(user_db).values(**data_as_dict)
    user_id = await database.execute(query)
    random_token = str(uuid4())
    query = insert(token_db).values(user_id=user_id, value=random_token)
    await database.execute(query)
    url = f"http://localhost:8000/api/verify-email?token={random_token}" # TODO: сделать функцию
    send_email("Подтверждение", data.email, url)
    data_as_dict.pop("password")
    return data_as_dict


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

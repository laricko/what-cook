from typing import Optional
from datetime import datetime, timedelta

from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request, HTTPException, status, Depends
from passlib.context import CryptContext
from jose.exceptions import JWTError
from jose import jwt
from sqlalchemy import select

from db.base import database
from db.user import users
from core.config import JWT_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from models.user import User


password_context = CryptContext("bcrypt", deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_passwrod(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)


def create_access_token(data: dict) -> str:
    to_encode = dict(data)
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)})
    token = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return token


def decode_access_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, ALGORITHM)
    except JWTError:
        return None


class JWTBearer(HTTPBearer):
    def __init__(self, *args, auto_eror: bool = True, **kwargs):
        super().__init__(*args, auto_error=auto_eror, **kwargs)

    async def __call__(
        self, request: Request
    ) -> Optional[HTTPAuthorizationCredentials]:
        exp = HTTPException(status.HTTP_400_BAD_REQUEST, "Invalid token")
        credentials = await super().__call__(request)
        if not credentials:
            raise exp
        else:
            data = decode_access_token(credentials.credentials)
            if data is None:
                raise exp
            return data


async def get_current_user(data: str = Depends(JWTBearer())) -> User:
    query = select(users).where(users.c.email == data.get("sub"))
    user = await database.fetch_one(query)
    return User.parse_obj(user)

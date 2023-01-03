from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: int
    email: EmailStr
    verified: bool

class UserLoginResponse(User):
    token: str

from uuid import uuid4

from sqlalchemy import insert

from db.base import database
from db.user import token
from utils.send_mail import send_email


async def send_email_verification(user_id: int, email: str) -> None:
    random_token = str(uuid4())
    query = insert(token).values(user_id=user_id, value=random_token)
    await database.execute(query)
    url = f"http://localhost:8000/api/verify-email?token={random_token}"  # TODO: сделать функцию
    send_email("Подтверждение", email, url)

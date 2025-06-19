from typing import Annotated
from fastapi import APIRouter, Depends
from openai import OpenAI

from api.dependencies import VerifiedTokenDep, DbDep, get_current_user
from core.config import settings
from dto.user import UserInDTO, UserOutDTO
from models.user import User


router = APIRouter()
client = OpenAI(api_key=settings.OPENAI_API_KEY)


@router.post("/users", response_model=UserOutDTO, status_code=201)
async def create_user(user_in: UserInDTO, db: DbDep, internal_token: VerifiedTokenDep):
    """
    Endpoint to create a new user.
    """
    user = User(
        telegram_id=user_in.telegram_id,
        name=user_in.name
    )
    db.add(user)
    await db.commit()
    return user


@router.get("/users/me", response_model=UserOutDTO)
async def get_current_user_info(user: Annotated[User, Depends(get_current_user)]):
    """
    Endpoint to get the current user's information.
    """
    return user
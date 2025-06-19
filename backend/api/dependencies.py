from typing import Annotated
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from core.config import settings

from fastapi import Depends, HTTPException, Header

from models.user import User


DbDep = Annotated[AsyncSession, Depends(get_session)]

async def get_current_user(
        db: DbDep,
        x_internal_token: Annotated[str | None, Header()] = None,
        x_telegram_user_id: Annotated[int | None, Header()] = None,
    ):
    """
    Dependency to get the current user based on the provided headers.
    """
    print(x_internal_token, x_telegram_user_id)
    if x_internal_token and x_telegram_user_id and x_internal_token == settings.INTERNAL_TOKEN:
        query = select(User).where(
            User.telegram_id == x_telegram_user_id
        )
        result = await db.scalars(query)
        user = result.one_or_none()
        if user:
            return user
    
    raise HTTPException(status_code=401, detail="Unauthorized: Invalid token or user ID")


async def get_current_active_user(
        user: Annotated[User, Depends(get_current_user)],
    ):
    """
    Dependency to get the current active user based on the provided headers.
    """
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Forbidden: User is not active")
    
    return user
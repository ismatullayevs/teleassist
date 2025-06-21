from typing import Annotated

from core.config import settings
from core.db import get_session
from fastapi import Depends, Header, HTTPException
from models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

DbDep = Annotated[AsyncSession, Depends(get_session)]


async def get_verified_internal_token(
    x_internal_token: Annotated[str, Header()],
):
    """
    Dependency to verify the internal token.
    """
    if x_internal_token != settings.INTERNAL_TOKEN:
        raise HTTPException(
            status_code=401, detail="Unauthorized: Invalid internal token"
        )
    return x_internal_token


VerifiedTokenDep = Annotated[str, Depends(get_verified_internal_token)]


async def get_current_user(
    db: DbDep,
    x_internal_token: Annotated[str | None, Header()] = None,
    x_telegram_user_id: Annotated[int | None, Header()] = None,
):
    """
    Dependency to get the current user based on the provided headers.
    """
    if (
        x_internal_token
        and x_telegram_user_id
        and x_internal_token == settings.INTERNAL_TOKEN
    ):
        query = select(User).where(User.telegram_id == int(x_telegram_user_id))
        result = await db.scalars(query)
        user = result.one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    raise HTTPException(status_code=401, detail="Unauthorized: Invalid internal token")


async def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)],
):
    """
    Dependency to get the current active user based on the provided headers.
    """
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Forbidden: User is not active")

    return user

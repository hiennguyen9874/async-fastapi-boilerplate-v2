from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, usecase
from app.core.settings import settings
from app.db.session import async_session

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="api/v0/auth/access-token")


async def get_db() -> AsyncGenerator:
    """
    Dependency function that yields db sessions
    """
    async with async_session() as session:
        yield session
        await session.commit()


async def get_redis(request: Request) -> redis.Redis:
    """
    Dependency function that yields redis connection
    """
    if not hasattr(request.app.state, "connection"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="connection attribute not set on app state",
        )
    return request.app.state.connection


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    user_id = usecase.user.parse_id_from_token(
        token=token, secret_key=settings.JWT.ACCESS_TOKEN_SECRET_KEY
    )

    user = await usecase.user.get(db=db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="The user doesn't have enough privileges"
        )
    return current_user

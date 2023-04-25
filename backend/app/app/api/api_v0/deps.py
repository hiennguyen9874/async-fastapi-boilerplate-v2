from typing import AsyncGenerator

import redis.asyncio as redis
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, usecase
from app.core.settings import settings
from app.db.session import async_session
from app.utils import errors

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
        raise errors.ErrInternalServerError("can not connect to redis")
    return request.app.state.connection


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    connection: redis.Redis = Depends(get_redis),
    token: str = Depends(reusable_oauth2),
) -> models.User:
    user_id = usecase.user.parse_id_from_token(
        token=token, secret_key=settings.JWT.ACCESS_TOKEN_SECRET_KEY
    )

    user = await usecase.user.get(db=db, connection=connection, id=user_id)
    if not user:
        raise errors.ErrNotFound("user not found")

    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise errors.ErrInactiveUser("inactive user")
    return current_user


async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_superuser:
        raise errors.ErrNotEnoughPrivileges("user doesn't have enough privileges")
    return current_user

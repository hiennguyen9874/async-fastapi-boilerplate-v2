from typing import Annotated, Any

import redis.asyncio as redis
from fastapi import APIRouter, Depends, Header, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, usecase
from app.api.api_v0 import deps

router = APIRouter()


@router.post("/access-token", response_model=schemas.Token)
async def login_access_token(
    *,
    db: AsyncSession = Depends(deps.get_db),
    connection: redis.Redis = Depends(deps.get_redis),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    access_token, refresh_token, _ = await usecase.user.sign_in(
        db=db, connection=connection, email=form_data.username, password=form_data.password
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/test-token", response_model=schemas.SuccessfulResponse[schemas.User])
async def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    # return current_user

    return schemas.create_successful_response(current_user)


@router.get("/refresh", response_model=schemas.Token)
async def refresh_token(
    *,
    db: AsyncSession = Depends(deps.get_db),
    connection: redis.Redis = Depends(deps.get_redis),
    refresh_token: Annotated[str, Header()],
) -> Any:
    access_token, refresh_token, _ = await usecase.user.refresh_token(
        db=db, connection=connection, refresh_token=refresh_token
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    *,
    connection: redis.Redis = Depends(deps.get_redis),
    refresh_token: Annotated[str, Header()],
) -> None:
    await usecase.user.logout(connection=connection, refresh_token=refresh_token)


@router.get("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
async def logout_all(
    *,
    connection: redis.Redis = Depends(deps.get_redis),
    refresh_token: Annotated[str, Header()],
) -> None:
    await usecase.user.logout_all_with_token(connection=connection, refresh_token=refresh_token)

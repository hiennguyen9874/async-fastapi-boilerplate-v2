from typing import Any

import redis.asyncio as redis
from fastapi import APIRouter, Depends
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

    return schemas.SuccessfulResponse(data=current_user, status=schemas.Status.success)

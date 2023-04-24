from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, usecase
from app.api.api_v0 import deps
from app.core import security
from app.core.settings import settings

router = APIRouter()


@router.post("/access-token", response_model=schemas.Token)
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user, found_user = await usecase.user.authenticate(
        db, email=form_data.username, password=form_data.password
    )

    if not found_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    access_token_expires = timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_DURATION)

    return {
        "access_token": security.create_access_token(user.id, expires_delta=access_token_expires),
        "token_type": "bearer",
    }


@router.post("/test-token", response_model=schemas.SuccessfulResponse[schemas.User])
async def test_token(current_user: models.User = Depends(deps.get_current_user)) -> Any:
    """
    Test access token
    """
    # return current_user

    return schemas.SuccessfulResponse(data=current_user, status=schemas.Status.success)

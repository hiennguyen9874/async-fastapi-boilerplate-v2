from typing import Annotated, Any

import redis.asyncio as redis
from fastapi import APIRouter, Body, Depends
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, usecase
from app.api.api_v0 import deps
from app.core.settings import settings
from app.utils import errors
from app.utils.encoders import jsonable_encoder_sqlalchemy

router = APIRouter()

CurrentUser = Annotated[models.User, Depends(deps.get_current_active_user)]
CurrentSuperUser = Annotated[models.User, Depends(deps.get_current_active_superuser)]


@router.get("/", response_model=schemas.SuccessfulResponse[list[schemas.User]])
async def read_users(
    *,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentSuperUser,  # pylint: disable=unused-argument
) -> Any:
    """
    Retrieve users.
    """
    return schemas.create_successful_response(
        await usecase.user.get_multi(db, offset=skip, limit=limit)
    )


@router.post("/", response_model=schemas.SuccessfulResponse[schemas.User])
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
    current_user: CurrentSuperUser,  # pylint: disable=unused-argument
) -> Any:
    """
    Create new user.
    """
    user = await usecase.user.get_by_email(db, email=user_in.email)
    if user:
        raise errors.ErrExistsEmail("email already exists")
    user = await usecase.user.create(db, **user_in.dict())

    # TODO: Send email # pylint: disable=fixme
    return schemas.create_successful_response(user)


@router.put("/me", response_model=schemas.SuccessfulResponse[schemas.User])
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    connection: redis.Redis = Depends(deps.get_redis),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: CurrentUser,
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder_sqlalchemy(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = await usecase.user.update(
        db=db, connection=connection, db_obj=current_user, obj_in=user_in
    )
    return schemas.create_successful_response(user)


@router.get("/me", response_model=schemas.SuccessfulResponse[schemas.User])
async def read_user_me(
    *,
    current_user: CurrentUser,
) -> Any:
    """
    Get current user.
    """
    return schemas.create_successful_response(current_user)


@router.post("/open", response_model=schemas.SuccessfulResponse[schemas.User])
async def create_user_open(
    *,
    db: AsyncSession = Depends(deps.get_db),
    password: str = Body(...),
    email: EmailStr = Body(...),
    full_name: str = Body(None),
) -> Any:
    """
    Create new user without the need to be logged in.
    """
    if not settings.USER.OPEN_REGISTRATION:
        raise errors.ErrApiDisable("open user registration not enable")
    user = await usecase.user.get_by_email(db, email=email)
    if user:
        raise errors.ErrExistsEmail("email already exists")
    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = await usecase.user.create(db, **user_in.dict())
    return schemas.create_successful_response(user)


@router.get("/{user_id}", response_model=schemas.SuccessfulResponse[schemas.User])
async def read_user_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    connection: redis.Redis = Depends(deps.get_redis),
    user_id: int,
    current_user: CurrentUser,
) -> Any:
    """
    Get a specific user by id.
    """
    user = await usecase.user.get(db=db, connection=connection, id=user_id)
    if not user:
        raise errors.ErrNotFound("user not found")
    if user.id == current_user.id:
        return schemas.create_successful_response(user)
    if not current_user.is_superuser:
        raise errors.ErrNotEnoughPrivileges("not enough permissions")
    return schemas.create_successful_response(user)


@router.put("/{user_id}", response_model=schemas.SuccessfulResponse[schemas.User])
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    connection: redis.Redis = Depends(deps.get_redis),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: CurrentSuperUser,  # pylint: disable=unused-argument
) -> Any:
    """
    Update a user.
    """
    user = await usecase.user.get(db=db, connection=connection, id=user_id)
    if not user:
        raise errors.ErrNotFound("user not found")
    user = await usecase.user.update(db=db, connection=connection, db_obj=user, obj_in=user_in)
    return schemas.create_successful_response(user)

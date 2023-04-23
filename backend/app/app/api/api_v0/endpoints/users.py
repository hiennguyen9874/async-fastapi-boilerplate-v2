from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, usecase
from app.api.api_v0 import deps
from app.core.settings import settings

router = APIRouter()

CurrentUser = Annotated[models.User, Depends(deps.get_current_active_user)]
CurrentSuperUser = Annotated[models.User, Depends(deps.get_current_active_superuser)]


@router.get("/", response_model=list[schemas.User])
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
    return await usecase.user.get_multi(db, offset=skip, limit=limit)


@router.post("/", response_model=schemas.User)
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
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await usecase.user.create(db, **user_in.dict())

    # TODO: Send email # pylint: disable=fixme
    return user


@router.put("/me", response_model=schemas.User)
async def update_user_me(
    *,
    db: AsyncSession = Depends(deps.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: CurrentUser,
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = await usecase.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.get("/me", response_model=schemas.User)
async def read_user_me(
    *,
    current_user: CurrentUser,
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.post("/open", response_model=schemas.User)
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
    if not settings.USER_OPEN_REGISTRATION:
        raise HTTPException(
            status_code=403,
            detail="Open user registration is forbidden on this server",
        )
    user = await usecase.user.get_by_email(db, email=email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system",
        )
    user_in = schemas.UserCreate(password=password, email=email, full_name=full_name)
    user = await usecase.user.create(db, **user_in.dict())
    return user


@router.get("/{user_id}", response_model=schemas.User)
async def read_user_by_id(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    current_user: CurrentUser,
) -> Any:
    """
    Get a specific user by id.
    """
    user = await usecase.user.get(db, id=user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return user


@router.put("/{user_id}", response_model=schemas.User)
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: CurrentSuperUser,  # pylint: disable=unused-argument
) -> Any:
    """
    Update a user.
    """
    user = await usecase.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = await usecase.user.update(db, db_obj=user, obj_in=user_in)
    return user

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas, usecase
from app.api.api_v0 import deps
from app.utils import errors

router = APIRouter()

CurrentUser = Annotated[models.User, Depends(deps.get_current_active_user)]
CurrentSuperUser = Annotated[models.User, Depends(deps.get_current_active_superuser)]


@router.get("/", response_model=schemas.SuccessfulResponse[list[schemas.Item]])
async def read_items(
    *,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: CurrentUser,
) -> Any:
    """
    Retrieve items.
    """
    return schemas.create_successful_response(
        await usecase.item.get_multi(db, offset=skip, limit=limit)
        if current_user.is_superuser
        else await usecase.item.get_multi_by_owner(
            db=db, owner_id=current_user.id, offset=skip, limit=limit
        )
    )


@router.post("/", response_model=schemas.SuccessfulResponse[schemas.Item])
async def create_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    item_in: schemas.ItemCreate,
    current_user: CurrentUser,
) -> Any:
    """
    Create new item.
    """
    item = await usecase.item.create_with_owner(db=db, obj_in=item_in, owner_id=current_user.id)
    return schemas.create_successful_response(item)


@router.put("/{id}", response_model=schemas.SuccessfulResponse[schemas.Item])
async def update_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,  # pylint: disable=redefined-builtin
    item_in: schemas.ItemUpdate,
    current_user: CurrentUser,
) -> Any:
    """
    Update an item.
    """
    item = await usecase.item.get(db=db, id=id)
    if not item:
        raise errors.ErrNotFound("item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise errors.ErrNotEnoughPrivileges("not enough permissions")
    item = await usecase.item.update(db=db, db_obj=item, obj_in=item_in)
    return schemas.create_successful_response(item)


@router.get("/{id}", response_model=schemas.SuccessfulResponse[schemas.Item])
async def read_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,  # pylint: disable=redefined-builtin
    current_user: CurrentUser,
) -> Any:
    """
    Get item by ID.
    """
    item = await usecase.item.get(db=db, id=id)
    if not item:
        raise errors.ErrNotFound("item not found")
    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise errors.ErrNotEnoughPrivileges("not enough permissions")
    return schemas.create_successful_response(item)


@router.delete("/{id}", response_model=schemas.SuccessfulResponse[schemas.Item])
async def delete_item(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,  # pylint: disable=redefined-builtin
    current_user: CurrentUser,
) -> Any:
    """
    Delete an item.
    """
    item = await usecase.item.get(db=db, id=id)

    if not item:
        raise errors.ErrNotFound("item not found")

    if not current_user.is_superuser and (item.owner_id != current_user.id):
        raise errors.ErrNotEnoughPrivileges("not enough permissions")

    return schemas.create_successful_response(await usecase.item.delete(db=db, db_obj=item))

from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item
from app.pg_repository.repository_item import item as repository_item
from app.pg_repository.repository_item import PgRepositoryItem
from app.schemas.item import ItemCreate, ItemUpdate
from app.usecase.base import UseCaseBase
from app.utils.encoders import jsonable_encoder_sqlalchemy


class UseCaseItem(UseCaseBase[Item, PgRepositoryItem, ItemCreate, ItemUpdate]):
    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Item]:
        return await self.pg_repository.get_multi_by_owner(
            db=db, owner_id=owner_id, offset=offset, limit=limit
        )

    async def create_with_owner(
        self, db: AsyncSession, *, obj_in: ItemCreate, owner_id: int
    ) -> Item:
        obj_in_data = jsonable_encoder_sqlalchemy(obj_in)
        db_obj = self.model(**obj_in_data, owner_id=owner_id)  # type: ignore
        return await self.pg_repository.create(db=db, db_obj=db_obj)


item = UseCaseItem(Item, repository_item)

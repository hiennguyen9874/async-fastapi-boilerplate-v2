from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Item
from app.pg_repository.base import PgRepositoryBase


class PgRepositoryItem(PgRepositoryBase[Item]):
    async def get_multi_by_owner(
        self,
        db: AsyncSession,
        *,
        owner_id: int,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Item]:
        q = await db.execute(
            select(self.model)
            .where(self.model.owner_id == owner_id)
            .offset(offset)
            .limit(limit)
            .order_by(self.model.id)
        )
        return q.scalars().all()


item = PgRepositoryItem(Item)

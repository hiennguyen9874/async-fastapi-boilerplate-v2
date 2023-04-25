from typing import Any

from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import User
from app.pg_repository.base import PgRepositoryBase


class PgRepositoryUser(PgRepositoryBase[User]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        q = await db.execute(select(self.model).where(self.model.email == email))
        return q.scalars().one_or_none()

    async def get_or_create_by_email(
        self, db: AsyncSession, *, email: str, **kwargs: dict[str, Any] | None
    ) -> tuple[User, bool]:
        obj = await self.get_by_email(db=db, email=email)
        if obj:
            return obj, False

        try:
            obj = self.model(email=email, **kwargs)  # type: ignore
            obj = await self.create(db=db, db_obj=obj)
            return obj, True
        except exc.IntegrityError:
            await db.rollback()
            q = await db.execute(select(self.model).where(self.model.email == email))
            obj = q.scalars().one()
            return obj, False


user = PgRepositoryUser(User)

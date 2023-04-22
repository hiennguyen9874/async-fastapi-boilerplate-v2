from typing import Any, AsyncIterator, Generic, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base
from app.pg_repository.base import PgRepositoryBase

ModelType = TypeVar("ModelType", bound=Base)
PgRepositoryType = TypeVar("PgRepositoryType", bound=PgRepositoryBase)


class UseCaseBase(Generic[ModelType, PgRepositoryType]):
    def __init__(self, model: Type[ModelType], repository: PgRepositoryType) -> None:
        self.model = model
        self.repository = repository

    async def get(
        self, db: AsyncSession, id: int  # pylint: disable=redefined-builtin
    ) -> ModelType | None:
        return await self.repository.get(db=db, id=id)

    async def get_all(self, db: AsyncSession) -> AsyncIterator[ModelType]:
        return await self.repository.get_all(db=db)

    async def create(self, db: AsyncSession, db_obj: ModelType) -> ModelType:
        return await self.repository.create(db=db, db_obj=db_obj)

    async def delete(self, db: AsyncSession, db_obj: ModelType) -> ModelType:
        return await self.repository.delete(db=db, db_obj=db_obj)

    async def delete_by_id(
        self, db: AsyncSession, id: int  # pylint: disable=redefined-builtin
    ) -> None:
        await self.repository.delete_by_id(db=db, id=id)

    async def delete_all(self, db: AsyncSession) -> None:
        await self.repository.delete_all(db=db)

    async def update(
        self, db: AsyncSession, db_obj: ModelType, update_data: dict[str, Any]
    ) -> ModelType:
        return await self.repository.update(db=db, db_obj=db_obj, update_data=update_data)

    async def get_multi(
        self, db: AsyncSession, offset: int = 0, limit: int = 100
    ) -> AsyncIterator[ModelType]:
        return await self.repository.get_multi(db=db, offset=offset, limit=limit)

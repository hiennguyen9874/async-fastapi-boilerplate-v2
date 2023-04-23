from typing import Any, Generic, Sequence, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from sqlalchemy import delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import Select

from app.db.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)


class PgRepositoryBase(Generic[ModelType]):
    """
    CRUD object with default methods to Create, Read, Update, Delete (CRUD).
    **Parameters**
    * `model`: A SQLAlchemy model class
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(
        self, db: AsyncSession, id: int  # pylint: disable=redefined-builtin
    ) -> ModelType | None:
        q = await db.execute(select(self.model).where(self.model.id == id))
        return q.scalars().one_or_none()

    async def get_all(self, db: AsyncSession) -> Sequence[ModelType]:
        statement = select(self.model).order_by(self.model.id)
        q = await db.execute(statement)
        return q.scalars().all()

    async def create(self, db: AsyncSession, *, db_obj: ModelType) -> ModelType:
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, db_obj: ModelType) -> ModelType:
        await db.delete(db_obj)
        await db.commit()
        return db_obj

    async def delete_by_id(
        self, db: AsyncSession, *, id: int  # pylint: disable=redefined-builtin
    ) -> None:
        await db.execute(delete(self.model).where(self.model.id == id))  # type: ignore
        await db.commit()

    async def delete_all(self, db: AsyncSession) -> None:
        await db.execute(delete(self.model))  # type: ignore
        await db.commit()

    async def update(
        self, db: AsyncSession, *, db_obj: ModelType, update_data: dict[str, Any]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def get_multi(
        self, db: AsyncSession, *, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        statement = select(self.model).offset(offset).limit(limit).order_by(self.model.id)
        q = await db.execute(statement)
        return q.scalars().all()

    async def count(self, db: AsyncSession, query: Select) -> int:
        return await db.scalar(
            select(func.count()).select_from(  # pylint: disable=not-callable
                query.with_only_columns(self.model.id).subquery()  # type: ignore
            )
        )

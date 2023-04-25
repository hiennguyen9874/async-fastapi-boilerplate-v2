from typing import Any, Generic, Sequence, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base_class import Base
from app.pg_repository.base import PgRepositoryBase
from app.utils.encoders import jsonable_encoder_sqlalchemy

ModelType = TypeVar("ModelType", bound=Base)
PgRepositoryType = TypeVar("PgRepositoryType", bound=PgRepositoryBase)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class UseCaseBase(Generic[ModelType, PgRepositoryType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], pg_repository: PgRepositoryType) -> None:
        self.model = model
        self.pg_repository = pg_repository

    async def get(
        self, db: AsyncSession, id: int  # pylint: disable=redefined-builtin
    ) -> ModelType | None:
        return await self.pg_repository.get(db=db, id=id)

    async def get_all(self, db: AsyncSession) -> Sequence[ModelType]:
        return await self.pg_repository.get_all(db=db)

    async def create(self, db: AsyncSession, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder_sqlalchemy(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        return await self.pg_repository.create(db=db, db_obj=db_obj)

    async def delete(self, db: AsyncSession, db_obj: ModelType) -> ModelType:
        return await self.pg_repository.delete(db=db, db_obj=db_obj)

    async def delete_by_id(
        self, db: AsyncSession, id: int  # pylint: disable=redefined-builtin
    ) -> None:
        await self.pg_repository.delete_by_id(db=db, id=id)

    async def delete_all(self, db: AsyncSession) -> None:
        await self.pg_repository.delete_all(db=db)

    async def update(
        self, db: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType | dict[str, Any]
    ) -> ModelType:
        return await self.pg_repository.update(
            db=db,
            db_obj=db_obj,
            update_data=obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True),
        )

    async def get_multi(
        self, db: AsyncSession, offset: int = 0, limit: int = 100
    ) -> Sequence[ModelType]:
        return await self.pg_repository.get_multi(db=db, offset=offset, limit=limit)

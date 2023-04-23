from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.pg_repository.repository_user import PgRepositoryUser
from app.pg_repository.repository_user import user as repository_user
from app.schemas.user import UserCreate, UserUpdate
from app.usecase.base import UseCaseBase


class UseCaseUser(UseCaseBase[User, PgRepositoryUser, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        return await self.repository.get_by_email(db=db, email=email)

    async def get_or_create_by_email(
        self, db: AsyncSession, *, email: str, **kwargs: dict[str, Any] | None
    ) -> tuple[User, bool]:
        return await self.repository.get_or_create_by_email(db=db, email=email, **kwargs)

    async def create(  # pylint: disable=arguments-differ
        self, db: AsyncSession, *, obj_in: UserCreate
    ) -> User:
        db_obj = self.model(  # type: ignore
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active,
        )
        return await self.repository.create(db=db, db_obj=db_obj)

    async def update(
        self, db: AsyncSession, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await self.repository.update(db=db, db_obj=db_obj, update_data=update_data)

    async def authenticate(self, db: AsyncSession, *, email: str, password: str) -> User | None:
        obj = await self.get_by_email(db=db, email=email)
        if not obj:
            return None
        return obj if verify_password(password, obj.hashed_password) else None


user = UseCaseUser(User, repository_user)

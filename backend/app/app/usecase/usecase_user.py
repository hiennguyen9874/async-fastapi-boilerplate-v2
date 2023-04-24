from datetime import timedelta
from typing import Any, Type

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_token, get_password_hash, verify_password
from app.core.settings import settings
from app.models.user import User
from app.pg_repository.repository_user import PgRepositoryUser
from app.pg_repository.repository_user import user as pg_repository_user
from app.redis_repository.repository_user import RedisRepositoryUser
from app.redis_repository.repository_user import user as redis_repository_user
from app.schemas.user import UserCreate, UserUpdate
from app.usecase.base import UseCaseBase


class UseCaseUser(UseCaseBase[User, PgRepositoryUser, UserCreate, UserUpdate]):
    def __init__(
        self,
        model: Type[User],
        pg_repository: PgRepositoryUser,
        redis_repository: RedisRepositoryUser,
    ) -> None:
        super().__init__(model, pg_repository)
        self.redis_repository = redis_repository

    @staticmethod
    def _generate_redis_refresh_token(id: int) -> str:  # pylint: disable=redefined-builtin
        return f"RefreshToken:{id}"

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        return await self.pg_repository.get_by_email(db=db, email=email)

    async def get_or_create_by_email(
        self, db: AsyncSession, *, email: str, **kwargs: dict[str, Any] | None
    ) -> tuple[User, bool]:
        return await self.pg_repository.get_or_create_by_email(db=db, email=email, **kwargs)

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
        return await self.pg_repository.create(db=db, db_obj=db_obj)

    async def update(
        self, db: AsyncSession, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await self.pg_repository.update(db=db, db_obj=db_obj, update_data=update_data)

    async def authenticate(
        self, db: AsyncSession, *, email: str, password: str
    ) -> tuple[User | None, bool]:
        obj = await self.get_by_email(db=db, email=email)
        if not obj:
            return None, False
        return (obj, True) if verify_password(password, obj.hashed_password) else (None, True)

    def create_token(self, id: int) -> tuple[str, str]:  # pylint: disable=redefined-builtin
        access_token = create_token(
            id,
            secret_key=settings.JWT.ACCESS_TOKEN_SECRET_KEY,
            expires_delta=timedelta(minutes=settings.JWT.ACCESS_TOKEN_EXPIRE_DURATION),
        )
        refresh_token = create_token(
            id,
            secret_key=settings.JWT.REFRESH_TOKEN_SECRET_KEY,
            expires_delta=timedelta(minutes=settings.JWT.REFRESH_TOKEN_EXPIRE_DURATION),
        )
        return access_token, refresh_token


user = UseCaseUser(User, pg_repository_user, redis_repository_user)

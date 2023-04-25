from datetime import timedelta
from typing import Any, Type

from jose import exceptions, jwt
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_token, get_password_hash, verify_password
from app.core.settings import settings
from app.models.user import User
from app.pg_repository.repository_user import PgRepositoryUser
from app.pg_repository.repository_user import user as pg_repository_user
from app.redis_repository.repository_user import RedisRepositoryUser
from app.redis_repository.repository_user import user as redis_repository_user
from app.schemas.user import UserCreate, UserInDB, UserUpdate
from app.usecase.base import UseCaseBase
from app.utils import errors
from app.utils.encoders import jsonable_encoder_sqlalchemy


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
    def _generate_redis_user(id: int) -> str:  # pylint: disable=redefined-builtin
        return f"Cache:User:{id}"

    @staticmethod
    def _generate_redis_refresh_token(id: int) -> str:  # pylint: disable=redefined-builtin
        return f"RefreshToken:{id}"

    async def create_cache(self, connection: Redis, db_obj: User) -> None:
        user_in_db = UserInDB.from_orm(db_obj)
        await self.redis_repository.create(
            connection=connection, key=self._generate_redis_user(db_obj.id), value=user_in_db.json()
        )

    async def get_cache(self, connection: Redis, obj_id: int) -> User | None:
        db_obj = await self.redis_repository.get(
            connection=connection, key=self._generate_redis_user(obj_id)
        )
        if not db_obj:
            return None
        user_in_db = UserInDB.parse_raw(db_obj)
        obj_in_data = jsonable_encoder_sqlalchemy(user_in_db)
        db_obj = User(**obj_in_data)  # type: ignore
        return db_obj

    async def get(
        self, db: AsyncSession, connection: Redis, id: int  # pylint: disable=redefined-builtin
    ) -> User | None:
        cached_user = await self.get_cache(connection=connection, obj_id=id)
        if cached_user is not None:
            return cached_user
        obj = await self.pg_repository.get(db=db, id=id)
        if not obj:
            return None
        await self.create_cache(connection=connection, db_obj=obj)
        return obj

    async def delete(self, db: AsyncSession, connection: Redis, db_obj: User) -> User:
        obj = await self.pg_repository.delete(db=db, db_obj=db_obj)

        await self.redis_repository.delete(
            connection=connection, key=self._generate_redis_user(db_obj.id)
        )

        await self.redis_repository.delete(
            connection=connection, key=self._generate_redis_refresh_token(db_obj.id)
        )

        return obj

    async def delete_by_id(
        self, db: AsyncSession, connection: Redis, id: int  # pylint: disable=redefined-builtin
    ) -> None:
        await self.pg_repository.delete_by_id(db=db, id=id)

        await self.redis_repository.delete(connection=connection, key=self._generate_redis_user(id))

        await self.redis_repository.delete(
            connection=connection, key=self._generate_redis_refresh_token(id)
        )

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        return await self.pg_repository.get_by_email(db=db, email=email)

    async def get_or_create_by_email(
        self, db: AsyncSession, *, email: str, **kwargs: dict[str, Any] | None
    ) -> tuple[User, bool]:
        return await self.pg_repository.get_or_create_by_email(db=db, email=email, **kwargs)

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = self.model(  # type: ignore
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            is_superuser=obj_in.is_superuser,
            is_active=obj_in.is_active,
        )
        return await self.pg_repository.create(db=db, db_obj=db_obj)

    async def update(
        self, db: AsyncSession, connection: Redis, db_obj: User, obj_in: UserUpdate | dict[str, Any]
    ) -> User:
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.dict(exclude_unset=True)
        if "password" in update_data and update_data["password"]:
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        obj = await self.pg_repository.update(db=db, db_obj=db_obj, update_data=update_data)

        await self.redis_repository.delete(
            connection=connection, key=self._generate_redis_user(db_obj.id)
        )

        await self.redis_repository.delete(
            connection=connection, key=self._generate_redis_refresh_token(db_obj.id)
        )

        return obj

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

    async def sign_in(
        self, db: AsyncSession, connection: Redis, *, email: str, password: str
    ) -> tuple[str, str, User]:
        obj = await self.get_by_email(db=db, email=email)
        if not obj:
            raise errors.ErrNotFound("user not found")

        if not verify_password(password, obj.hashed_password):
            raise errors.ErrWrongPassword("wrong password")

        if not obj.is_active:
            raise errors.ErrInactiveUser("inactive user")

        access_token, refresh_token = self.create_token(obj.id)

        await self.redis_repository.set_add(
            connection=connection,
            key=self._generate_redis_refresh_token(obj.id),
            value=refresh_token,
        )

        return access_token, refresh_token, obj

    def parse_id_from_token(self, token: str, secret_key: str) -> int:
        try:
            token_data = jwt.decode(token, secret_key, algorithms=[settings.JWT.ALGORITHM])
        except (exceptions.JWTError, ValidationError) as e:
            raise errors.ErrInvalidJWTToken("could not validate credentials") from e

        if "sub" not in token_data and token_data["sub"] is None:
            raise errors.ErrInvalidJWTToken("could not validate credentials")

        return int(token_data["sub"])

    async def refresh_token(
        self, db: AsyncSession, connection: Redis, *, refresh_token: str
    ) -> tuple[str, str, User]:
        obj_id = self.parse_id_from_token(
            token=refresh_token, secret_key=settings.JWT.REFRESH_TOKEN_SECRET_KEY
        )

        if not await self.redis_repository.set_is_member(
            connection=connection,
            key=self._generate_redis_refresh_token(obj_id),
            value=refresh_token,
        ):
            raise errors.ErrNotFoundRefreshTokenRedis("not found refresh token")

        await self.redis_repository.set_delete(
            connection=connection,
            key=self._generate_redis_refresh_token(obj_id),
            value=refresh_token,
        )

        obj = await self.get(db=db, connection=connection, id=obj_id)
        if obj is None:
            raise errors.ErrNotFound("not found user")

        access_token, refresh_token = self.create_token(obj.id)

        await self.redis_repository.set_add(
            connection=connection,
            key=self._generate_redis_refresh_token(obj.id),
            value=refresh_token,
        )

        return access_token, refresh_token, obj

    async def logout(self, connection: Redis, refresh_token: str) -> None:
        obj_id = self.parse_id_from_token(
            token=refresh_token, secret_key=settings.JWT.REFRESH_TOKEN_SECRET_KEY
        )
        await self.redis_repository.set_delete(
            connection=connection,
            key=self._generate_redis_refresh_token(obj_id),
            value=refresh_token,
        )

    async def logout_all(self, connection: Redis, obj_id: int) -> None:
        await self.redis_repository.delete(
            connection=connection, key=self._generate_redis_refresh_token(obj_id)
        )

    async def logout_all_with_token(self, connection: Redis, refresh_token: str) -> None:
        await self.logout_all(
            connection=connection,
            obj_id=self.parse_id_from_token(
                token=refresh_token, secret_key=settings.JWT.REFRESH_TOKEN_SECRET_KEY
            ),
        )


user = UseCaseUser(User, pg_repository_user, redis_repository_user)

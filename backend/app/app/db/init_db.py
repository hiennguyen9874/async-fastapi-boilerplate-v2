from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, usecase
from app.core.settings import settings
from app.db import base  # type: ignore # noqa: F401 # pylint: disable=unused-import

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


async def init_db(db: AsyncSession) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)

    user = await usecase.user.get_by_email(db, email=settings.FIRST_SUPERUSER.EMAIL)

    if not user:
        user = await usecase.user.create(
            db=db,
            obj_in=schemas.UserCreate(
                email=settings.FIRST_SUPERUSER.EMAIL,
                password=settings.FIRST_SUPERUSER.PASSWORD,
                full_name=settings.FIRST_SUPERUSER.NAME,
                is_superuser=True,
            ),
        )

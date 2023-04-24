from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

async_engine = create_async_engine(
    settings.ASYNC_SQLALCHEMY_DATABASE_URI,  # type: ignore
    echo=settings.SQLALCHEMY_ECHO,
    pool_pre_ping=True,
    future=True,
)
async_session = async_sessionmaker(async_engine, expire_on_commit=False)

engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URI,  # type: ignore
    echo=settings.SQLALCHEMY_ECHO,
    pool_pre_ping=True,
    future=True,
)
session = sessionmaker(engine, autocommit=False, autoflush=False)

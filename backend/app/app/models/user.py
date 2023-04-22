from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.utils import TZDateTime

__all__ = ["User"]


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    full_name = Column(String, index=False, nullable=True)
    created_at = Column(TZDateTime, default=func.now())  # pylint: disable=not-callable
    updated_at = Column(TZDateTime, onupdate=func.now())  # pylint: disable=not-callable

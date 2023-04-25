from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.utils import TZDateTime

if TYPE_CHECKING:
    from .item import Item  # noqa: F401

__all__ = ["User"]


class User(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_superuser: Mapped[bool] = mapped_column(default=False)
    email: Mapped[str] = mapped_column(unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=True)
    full_name: Mapped[str | None] = mapped_column(index=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=func.now()  # pylint: disable=not-callable
    )  # pylint: disable=not-callable
    updated_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=func.now(), onupdate=func.now()  # pylint: disable=not-callable
    )  # pylint: disable=not-callable
    items: Mapped[list[Item]] = relationship(back_populates="owner", lazy="select")

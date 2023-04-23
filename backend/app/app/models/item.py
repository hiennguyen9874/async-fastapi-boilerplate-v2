from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.utils import TZDateTime

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Item(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str | None] = mapped_column(index=True)
    description: Mapped[str | None] = mapped_column(index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    owner: Mapped[User] = relationship(back_populates="items", lazy="select")
    created_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=func.now()  # pylint: disable=not-callable
    )
    updated_at: Mapped[datetime] = mapped_column(
        TZDateTime, default=func.now(), onupdate=func.now()  # pylint: disable=not-callable
    )

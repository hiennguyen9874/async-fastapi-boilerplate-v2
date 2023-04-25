from typing import Any

from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    id: Any

    # Generate __tablename__ automatically
    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa B904 pylint: disable=no-self-argument
        # sourcery skip: instance-method-first-arg-name
        return cls.__name__.lower()

    # required in order to access columns with server defaults
    # or SQL expression defaults, subsequent to a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}

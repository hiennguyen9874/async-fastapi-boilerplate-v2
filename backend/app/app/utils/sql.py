# pylint: skip-file
from datetime import datetime, timezone
from typing import Any, Union

import pytz
from sqlalchemy import DateTime, TypeDecorator
from sqlalchemy.engine import Dialect

from app.core.settings import settings

__all__ = ["TZDateTime"]


class TZDateTime(TypeDecorator):
    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: Union[datetime, None], dialect: Dialect) -> Any:
        if value is not None:
            if not value.tzinfo:
                raise TypeError("tzinfo is required")
            value = value.astimezone(timezone.utc).replace(tzinfo=None)
        return value

    def process_result_value(self, value: Union[datetime, None], dialect: Dialect) -> Any:
        if value is not None:
            value = value.replace(tzinfo=timezone.utc).astimezone(
                pytz.timezone(settings.APP_TIMEZONE)
            )
        return value

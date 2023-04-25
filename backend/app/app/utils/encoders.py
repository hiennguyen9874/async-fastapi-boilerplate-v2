import datetime
import decimal
import uuid
from typing import Any, Callable

from fastapi.encoders import DictIntStrAny, jsonable_encoder, SetIntStr


def jsonable_encoder_sqlalchemy(  # pylint: disable=too-many-arguments
    obj: Any,
    include: SetIntStr | DictIntStrAny | None = None,
    exclude: SetIntStr | DictIntStrAny | None = None,
    by_alias: bool = True,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    custom_encoder: dict[Any, Callable[[Any], Any]] | None = None,
    sqlalchemy_safe: bool = True,
) -> Any:
    sqlalchemy_custom_encoder = {
        bool: lambda x: x,
        bytes: lambda x: x,
        datetime.date: lambda x: x,
        datetime.datetime: lambda x: x,
        datetime.time: lambda x: x,
        datetime.timedelta: lambda x: x,
        decimal.Decimal: lambda x: x,
        float: lambda x: x,
        int: lambda x: x,
        str: lambda x: x,
        uuid.UUID: lambda x: x,
    }
    if custom_encoder is not None:
        sqlalchemy_custom_encoder = {**sqlalchemy_custom_encoder, **custom_encoder}
    return jsonable_encoder(
        obj=obj,
        include=include,
        exclude=exclude,
        by_alias=by_alias,
        exclude_unset=exclude_unset,
        exclude_defaults=exclude_defaults,
        exclude_none=exclude_none,
        custom_encoder=sqlalchemy_custom_encoder,
        sqlalchemy_safe=sqlalchemy_safe,
    )

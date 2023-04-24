from enum import Enum
from typing import Any, Annotated

from fastapi import APIRouter, Depends
from loguru import logger

from app import models, schemas
from app.api.api_v0 import deps
from app.tasks import test_celery as test_celery_task

router = APIRouter()


CurrentSuperUser = Annotated[models.User, Depends(deps.get_current_active_superuser)]


@router.post("/test-celery", response_model=schemas.Msg, status_code=201)
async def test_celery(
    *,
    msg: schemas.Msg,
    current_user: CurrentSuperUser,  # pylint: disable=unused-argument
) -> Any:
    """
    Test Celery worker.
    """
    task = test_celery_task.delay(msg.msg)
    task.get()
    return {"msg": "Word received"}


class LoguruLevel(str, Enum):
    info = "info"
    debug = "debug"
    warning = "warning"
    error = "error"
    critical = "critical"


@router.post("/test-loguru", status_code=201)
async def test_loguru(
    *,
    msg: schemas.Msg,
    level: LoguruLevel,
    current_user: CurrentSuperUser,  # pylint: disable=unused-argument
) -> Any:
    """
    Test loguru.
    """

    if level == LoguruLevel.info:
        logger.info(msg.msg)
    elif level == LoguruLevel.debug:
        logger.debug(msg.msg)
    elif level == LoguruLevel.warning:
        logger.warning(msg.msg)
    elif level == LoguruLevel.error:
        logger.error(msg.msg)
    elif level == LoguruLevel.critical:
        logger.critical(msg.msg)

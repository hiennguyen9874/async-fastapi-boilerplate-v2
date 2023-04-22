import logging
from pathlib import Path

import sentry_sdk
from celery.signals import setup_logging
from sentry_sdk.integrations.celery import CeleryIntegration

from app.core.celery_app import celery_app
from app.core.settings import settings
from app.custom_logging import CustomizeLogger

if settings.SENTRY_DSN is not None:
    sentry_sdk.init(
        settings.SENTRY_DSN,
        environment=settings.SENTRY_ENVIRONMENT,
        integrations=[CeleryIntegration()],
    )


@setup_logging.connect()
def config_loggers(*args, **kwargs) -> logging.Logger:  # type: ignore # pylint: disable=unused-argument
    return CustomizeLogger.make_logger(Path(__file__).with_name("worker_logging.json"))


celery = celery_app

from celery import Celery

from app.core.settings import settings

celery_app = Celery(
    "worker",
    broker_url=settings.CELERY.BROKER_URL,
    result_backend=settings.CELERY.RESULT_BACKEND,
    result_serializer=settings.CELERY.RESULT_SERIALIZER,
    task_serializer=settings.CELERY.TASK_SERIALIZER,
    accept_content=settings.CELERY.ACCEPT_CONTENT,
    enable_utc=settings.CELERY.ENABLE_UTC,
    timezone=settings.CELERY.TIMEZONE,
    task_default_queue=settings.CELERY.DEFAULT_QUEUE,
    task_queues=settings.CELERY.QUEUES,
    imports=settings.CELERY.IMPORTS,
    beat_schedule=settings.CELERY.BEAT_SCHEDULE,
)

celery_app.autodiscover_tasks(["app"])

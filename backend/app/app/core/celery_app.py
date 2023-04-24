from celery import Celery

from app.core.settings import settings

celery_app = Celery(
    "worker",
    broker_url=settings.CELERY.BROKER_URL,
    result_backend=settings.CELERY.RESULT_BACKEND,
)

celery_app.config_from_object(settings, namespace="CELERY")
celery_app.autodiscover_tasks(["app"])

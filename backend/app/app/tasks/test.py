from loguru import logger

from app.core.celery_app import celery_app

__all__ = ["test_celery", "task_schedule_work"]


@celery_app.task(name="test_celery")
def test_celery(word: str) -> str:
    return f"test task return {word}"


@celery_app.task(name="task_schedule_work")
def task_schedule_work() -> None:
    logger.info("task_schedule_work run")

# backend/celery_app.py
import os
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    settings.PROJECT_NAME,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_extended=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    broker_pool_limit=5,
    worker_concurrency=4,
)

# auto-discover tasks in app.tasks modules
celery_app.autodiscover_tasks(["app.tasks"])

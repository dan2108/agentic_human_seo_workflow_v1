from celery import Celery
import os

celery_app = Celery(
    "agentic_seo",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "monitor-daily": {"task": "app.workers.tasks.run_monitor", "schedule": 86400},
    },
)

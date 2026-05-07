from app.workers.celery_app import celery_app
import structlog

log = structlog.get_logger()


@celery_app.task(name="app.workers.tasks.run_day7_check")
def run_day7_check(job_id: str) -> None:
    log.info("celery.day7_check", job_id=job_id)
    raise NotImplementedError


@celery_app.task(name="app.workers.tasks.run_day30_check")
def run_day30_check(job_id: str) -> None:
    log.info("celery.day30_check", job_id=job_id)
    raise NotImplementedError


@celery_app.task(name="app.workers.tasks.run_day90_check")
def run_day90_check(job_id: str) -> None:
    log.info("celery.day90_check", job_id=job_id)
    raise NotImplementedError


@celery_app.task(name="app.workers.tasks.run_monitor")
def run_monitor() -> None:
    log.info("celery.monitor")
    raise NotImplementedError

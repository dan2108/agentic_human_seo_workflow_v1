import structlog

log = structlog.get_logger()


class AftercareOrchestrator:
    """Schedules Day 7 / 30 / 90 checks via Celery after publish."""

    async def schedule(self, job_id: str, published_at: str) -> None:
        log.info("aftercare_orchestrator.schedule", job_id=job_id)
        raise NotImplementedError

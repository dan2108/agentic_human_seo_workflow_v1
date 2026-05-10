from datetime import datetime, timedelta, timezone

import structlog

from app.workers.tasks import run_day7_check, run_day30_check, run_day90_check

log = structlog.get_logger()


class AftercareOrchestrator:
    """Schedules Day 7 / 30 / 90 checks via Celery after publish."""

    async def schedule(self, job_id: str, published_at: str) -> None:
        log.info("aftercare_orchestrator.schedule", job_id=job_id)
        base = datetime.fromisoformat(published_at)
        if base.tzinfo is None:
            base = base.replace(tzinfo=timezone.utc)

        run_day7_check.apply_async(args=[job_id], eta=base + timedelta(days=7))
        run_day30_check.apply_async(args=[job_id], eta=base + timedelta(days=30))
        run_day90_check.apply_async(args=[job_id], eta=base + timedelta(days=90))

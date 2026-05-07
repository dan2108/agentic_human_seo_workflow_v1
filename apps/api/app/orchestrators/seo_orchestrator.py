import structlog

log = structlog.get_logger()


class SEOOrchestrator:
    """Fans out work to Research and Track A after Gate 1 approval."""

    async def dispatch(self, job_id: str) -> None:
        log.info("seo_orchestrator.dispatch", job_id=job_id)
        raise NotImplementedError

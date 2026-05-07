import structlog

log = structlog.get_logger()


class ContentAuditAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("content_audit_agent.run", job_id=job_id)
        raise NotImplementedError

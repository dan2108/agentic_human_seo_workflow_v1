import structlog

log = structlog.get_logger()


class AnalyticsAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("analytics_agent.run", job_id=job_id)
        raise NotImplementedError

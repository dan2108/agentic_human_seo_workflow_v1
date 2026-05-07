import structlog

log = structlog.get_logger()


class OnPageAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("onpage_agent.run", job_id=job_id)
        raise NotImplementedError

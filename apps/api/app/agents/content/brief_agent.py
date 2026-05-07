import structlog

log = structlog.get_logger()


class BriefAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("brief_agent.run", job_id=job_id)
        raise NotImplementedError

import structlog

log = structlog.get_logger()


class CompetitiveAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("competitive_agent.run", job_id=job_id)
        raise NotImplementedError

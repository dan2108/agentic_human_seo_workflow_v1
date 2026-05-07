import structlog

log = structlog.get_logger()


class FactCheckAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("factcheck_agent.run", job_id=job_id)
        raise NotImplementedError

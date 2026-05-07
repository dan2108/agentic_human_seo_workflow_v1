import structlog

log = structlog.get_logger()


class DistributionAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("distribution_agent.run", job_id=job_id)
        raise NotImplementedError

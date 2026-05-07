import structlog

log = structlog.get_logger()


class Day90Agent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("day90_agent.run", job_id=job_id)
        raise NotImplementedError

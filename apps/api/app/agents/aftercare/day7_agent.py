import structlog

log = structlog.get_logger()


class Day7Agent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("day7_agent.run", job_id=job_id)
        raise NotImplementedError

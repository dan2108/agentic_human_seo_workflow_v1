import structlog

log = structlog.get_logger()


class Day30Agent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("day30_agent.run", job_id=job_id)
        raise NotImplementedError

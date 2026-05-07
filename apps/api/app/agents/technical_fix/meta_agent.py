import structlog

log = structlog.get_logger()


class MetaAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("meta_agent.run", job_id=job_id)
        raise NotImplementedError

import structlog

log = structlog.get_logger()


class OutlineAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("outline_agent.run", job_id=job_id)
        raise NotImplementedError

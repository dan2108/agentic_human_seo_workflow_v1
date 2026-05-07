import structlog

log = structlog.get_logger()


class LinkingAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("linking_agent.run", job_id=job_id)
        raise NotImplementedError

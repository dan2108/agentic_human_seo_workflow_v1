import structlog

log = structlog.get_logger()


class AuthorityAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("authority_agent.run", job_id=job_id)
        raise NotImplementedError

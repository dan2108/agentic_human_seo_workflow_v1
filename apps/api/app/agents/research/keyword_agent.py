import structlog

log = structlog.get_logger()


class KeywordAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("keyword_agent.run", job_id=job_id)
        raise NotImplementedError

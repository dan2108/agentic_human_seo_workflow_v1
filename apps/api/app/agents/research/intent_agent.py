import structlog

log = structlog.get_logger()


class IntentAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("intent_agent.run", job_id=job_id)
        raise NotImplementedError

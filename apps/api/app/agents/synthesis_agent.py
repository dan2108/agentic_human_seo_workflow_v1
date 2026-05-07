import structlog

log = structlog.get_logger()


class SynthesisAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("synthesis_agent.run", job_id=job_id)
        raise NotImplementedError

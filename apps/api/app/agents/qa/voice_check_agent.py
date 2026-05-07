import structlog

log = structlog.get_logger()


class VoiceCheckAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("voice_check_agent.run", job_id=job_id)
        raise NotImplementedError

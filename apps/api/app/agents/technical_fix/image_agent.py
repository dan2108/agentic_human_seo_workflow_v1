import structlog

log = structlog.get_logger()


class ImageAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("image_agent.run", job_id=job_id)
        raise NotImplementedError

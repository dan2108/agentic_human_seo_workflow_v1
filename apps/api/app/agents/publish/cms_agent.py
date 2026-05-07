import structlog

log = structlog.get_logger()


class CmsAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("cms_agent.run", job_id=job_id)
        raise NotImplementedError

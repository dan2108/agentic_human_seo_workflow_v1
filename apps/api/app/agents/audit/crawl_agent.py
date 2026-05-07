import structlog

log = structlog.get_logger()


class CrawlAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("crawl_agent.run", job_id=job_id)
        raise NotImplementedError

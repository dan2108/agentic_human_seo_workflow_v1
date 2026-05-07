import structlog

log = structlog.get_logger()


class CalendarAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("calendar_agent.run", job_id=job_id)
        raise NotImplementedError

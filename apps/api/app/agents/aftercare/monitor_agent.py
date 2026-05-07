import structlog

log = structlog.get_logger()


class MonitorAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("monitor_agent.run", job_id=job_id)
        raise NotImplementedError

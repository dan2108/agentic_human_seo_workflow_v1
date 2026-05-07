import structlog

log = structlog.get_logger()


class SchemaAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("schema_agent.run", job_id=job_id)
        raise NotImplementedError

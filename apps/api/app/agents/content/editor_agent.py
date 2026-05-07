import structlog

log = structlog.get_logger()


class EditorAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("editor_agent.run", job_id=job_id)
        raise NotImplementedError

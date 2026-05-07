import structlog

log = structlog.get_logger()


class PlagiarismAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("plagiarism_agent.run", job_id=job_id)
        raise NotImplementedError

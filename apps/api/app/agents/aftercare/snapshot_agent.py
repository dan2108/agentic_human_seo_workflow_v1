import structlog

log = structlog.get_logger()


class SnapshotAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("snapshot_agent.run", job_id=job_id)
        raise NotImplementedError

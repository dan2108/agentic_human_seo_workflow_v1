import structlog

log = structlog.get_logger()


class ClusterAgent:
    async def run(self, job_id: str, **kwargs) -> dict:
        log.info("cluster_agent.run", job_id=job_id)
        raise NotImplementedError

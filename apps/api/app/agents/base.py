from abc import ABC, abstractmethod
from typing import Any
import structlog

log = structlog.get_logger()


class BaseAuditAgent(ABC):
    def __init__(self, db: Any) -> None:
        self._db = db

    @abstractmethod
    async def run(self, job_id: str, site_url: str) -> dict[str, Any]: ...

    def _persist(self, job_id: str, stream: str, data: dict[str, Any]) -> dict[str, Any]:
        self._db.table("audit_results").upsert(
            {"job_id": job_id, "stream": stream, "data_json": data}
        ).execute()
        log.info("agent.persisted", job_id=job_id, stream=stream)
        return {"stream": stream, "data_json": data}

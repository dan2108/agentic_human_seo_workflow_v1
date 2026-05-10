from typing import Any
import httpx
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

INDEXING_API_URL = "https://indexing.googleapis.com/v3/urlNotifications:publish"


class IndexPingAgent(BaseAuditAgent):
    def __init__(self, db: Any, access_token: str) -> None:
        super().__init__(db)
        self._access_token = access_token

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("index_ping_agent.run", job_id=job_id, url=site_url)

        headers = {"Authorization": f"Bearer {self._access_token}", "Content-Type": "application/json"}
        payload = {"url": site_url, "type": "URL_UPDATED"}

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(INDEXING_API_URL, json=payload, headers=headers)

        status = "submitted" if resp.status_code == 200 else "failed"
        data = {"url": site_url, "status": status, "http_status": resp.status_code}
        return self._persist(job_id, "index_ping", data)

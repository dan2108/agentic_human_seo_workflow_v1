from typing import Any
import httpx
import structlog
from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

AHREFS_BASE = "https://api.ahrefs.com/v3"


class AuthorityAgent(BaseAuditAgent):
    def __init__(self, db: Any, ahrefs_api_key: str) -> None:
        super().__init__(db)
        self._api_key = ahrefs_api_key

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("authority_agent.run", job_id=job_id)
        domain = site_url.replace("https://", "").replace("http://", "").rstrip("/")

        headers = {"Authorization": f"Bearer {self._api_key}"}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(
                f"{AHREFS_BASE}/site-explorer/domain-rating",
                params={"target": domain, "mode": "domain"},
                headers=headers,
            )

        if resp.status_code == 200:
            raw = resp.json()
            data = {
                "domain_rating": raw.get("domain_rating", 0),
                "organic_traffic": raw.get("organic_traffic", 0),
                "referring_domains": raw.get("referring_domains", 0),
            }
        else:
            log.warning("authority_agent.ahrefs_error", status=resp.status_code)
            data = {"domain_rating": 0, "organic_traffic": 0, "referring_domains": 0, "error": f"HTTP {resp.status_code}"}

        return self._persist(job_id, "authority", data)

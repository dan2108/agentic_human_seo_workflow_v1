from typing import Any
import httpx
import structlog
from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

DATAFORSEO_BASE = "https://api.dataforseo.com/v3"


class CompetitiveAgent(BaseAuditAgent):
    def __init__(self, db: Any, dataforseo_login: str, dataforseo_password: str) -> None:
        super().__init__(db)
        self._auth = (dataforseo_login, dataforseo_password)

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("competitive_agent.run", job_id=job_id)
        domain = site_url.replace("https://", "").replace("http://", "").rstrip("/")

        payload = [{"target": domain, "location_code": 2840, "language_code": "en"}]
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{DATAFORSEO_BASE}/serp/google/organic/live/regular",
                auth=self._auth,
                json=payload,
            )

        ranked_keywords: list[dict] = []
        if resp.status_code == 200:
            tasks = resp.json().get("tasks", [])
            if tasks and tasks[0].get("result"):
                items = tasks[0]["result"][0].get("items", [])
                ranked_keywords = [
                    {"keyword": item.get("keyword"), "rank": item.get("rank_absolute")}
                    for item in items[:20]
                ]

        data = {
            "ranked_keywords": ranked_keywords,
            "ranked_keywords_count": len(ranked_keywords),
            "domain": domain,
        }
        return self._persist(job_id, "competitive", data)

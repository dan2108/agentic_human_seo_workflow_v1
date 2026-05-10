from typing import Any
import httpx
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

DATAFORSEO_SERP_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"


class SerpAgent(BaseAuditAgent):
    def __init__(self, db: Any, dataforseo_login: str, dataforseo_password: str) -> None:
        super().__init__(db)
        self._login = dataforseo_login
        self._password = dataforseo_password

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("serp_agent.run", job_id=job_id, site_url=site_url)

        domain = site_url.rstrip("/").split("//")[-1]
        payload = [{"keyword": domain, "location_code": 2840, "language_code": "en", "depth": 10}]

        async with httpx.AsyncClient(auth=(self._login, self._password), timeout=30) as client:
            resp = await client.post(DATAFORSEO_SERP_URL, json=payload)

        serp_results: list[dict[str, Any]] = []
        total_results = 0
        if resp.status_code == 200:
            tasks = resp.json().get("tasks", [])
            for task in tasks:
                for result in task.get("result", []):
                    total_results = result.get("se_results_count", 0)
                    for item in result.get("items", []):
                        serp_results.append({
                            "type": item.get("type", "organic"),
                            "title": item.get("title", ""),
                            "url": item.get("url", ""),
                            "rank_absolute": item.get("rank_absolute", 0),
                        })

        data = {"serp_results": serp_results, "total_results": total_results}
        return self._persist(job_id, "serp", data)

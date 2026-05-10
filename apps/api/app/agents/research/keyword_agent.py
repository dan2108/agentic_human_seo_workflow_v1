from typing import Any
import httpx
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

DATAFORSEO_KEYWORDS_URL = "https://api.dataforseo.com/v3/keywords_data/google_ads/search_volume/live"


class KeywordAgent(BaseAuditAgent):
    def __init__(self, db: Any, dataforseo_login: str, dataforseo_password: str) -> None:
        super().__init__(db)
        self._login = dataforseo_login
        self._password = dataforseo_password

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("keyword_agent.run", job_id=job_id, site_url=site_url)

        seed_keywords = [site_url.rstrip("/").split("//")[-1]]
        payload = [{"keywords": seed_keywords, "location_code": 2840, "language_code": "en"}]

        async with httpx.AsyncClient(auth=(self._login, self._password), timeout=30) as client:
            resp = await client.post(DATAFORSEO_KEYWORDS_URL, json=payload)

        keywords: list[dict[str, Any]] = []
        if resp.status_code == 200:
            tasks = resp.json().get("tasks", [])
            for task in tasks:
                for result in task.get("result", []):
                    for item in result.get("items", []):
                        keywords.append({
                            "keyword": item.get("keyword", ""),
                            "search_volume": item.get("search_volume", 0),
                            "keyword_difficulty": item.get("keyword_difficulty", 0),
                        })

        data = {"keywords": keywords, "keywords_count": len(keywords)}
        return self._persist(job_id, "keywords", data)

from typing import Any
import httpx
import structlog

from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

GSC_SEARCH_ANALYTICS = "https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
DATAFORSEO_SERP_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"


class SnapshotAgent(BaseAuditAgent):
    def __init__(self, db: Any, access_token: str, dataforseo_login: str, dataforseo_password: str) -> None:
        super().__init__(db)
        self._access_token = access_token
        self._dfs_login = dataforseo_login
        self._dfs_password = dataforseo_password

    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("snapshot_agent.run", job_id=job_id, site_url=site_url)

        encoded_site = site_url.rstrip("/").replace("://", "%3A//")
        gsc_url = GSC_SEARCH_ANALYTICS.format(site=encoded_site)
        gsc_headers = {"Authorization": f"Bearer {self._access_token}"}
        gsc_payload = {"startDate": "2026-01-01", "endDate": "2026-05-01", "dimensions": ["page"], "rowLimit": 10}

        dfs_payload = [{"keyword": site_url.split("//")[-1], "location_code": 2840, "language_code": "en", "depth": 5}]

        async with httpx.AsyncClient(timeout=30) as client:
            gsc_resp = await client.post(gsc_url, json=gsc_payload, headers=gsc_headers)
            dfs_resp = await client.post(DATAFORSEO_SERP_URL, json=dfs_payload, auth=(self._dfs_login, self._dfs_password))

        impressions = 0
        clicks = 0
        position = 0.0
        if gsc_resp.status_code == 200:
            rows = gsc_resp.json().get("rows", [])
            if rows:
                impressions = rows[0].get("impressions", 0)
                clicks = rows[0].get("clicks", 0)
                position = rows[0].get("position", 0.0)

        rank = 0
        if dfs_resp.status_code == 200:
            tasks = dfs_resp.json().get("tasks", [])
            for task in tasks:
                for result in task.get("result", []):
                    items = result.get("items", [])
                    if items:
                        rank = items[0].get("rank_absolute", 0)

        metrics = {
            "impressions": impressions,
            "clicks": clicks,
            "position": position,
            "rank": rank,
            "site_url": site_url,
        }

        self._db.table("baseline_snapshots").insert({
            "job_id": job_id,
            "url": site_url,
            "metrics_json": metrics,
        }).execute()

        return {"stream": "snapshot", "data_json": metrics}

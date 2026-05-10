"""Day 30 aftercare — rank trajectory + traffic delta + backlinks earned.

Runs 30 days after publish. Adds Ahrefs backlink data on top of the Day 7
GSC + DataForSEO checks. Writes to aftercare_reports with checkpoint='day30'.
"""
from typing import Any
import httpx
import structlog

log = structlog.get_logger()

GSC_SEARCH_ANALYTICS = "https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
DATAFORSEO_SERP_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
AHREFS_BACKLINKS_URL = "https://api.ahrefs.com/v3/site-explorer/backlinks"


class Day30Agent:
    def __init__(
        self,
        db: Any,
        access_token: str,
        dataforseo_login: str,
        dataforseo_password: str,
        ahrefs_api_key: str,
    ) -> None:
        self._db = db
        self._access_token = access_token
        self._dfs_login = dataforseo_login
        self._dfs_password = dataforseo_password
        self._ahrefs_key = ahrefs_api_key

    def _load_baseline(self, job_id: str) -> dict[str, Any]:
        row = (
            self._db.table("baseline_snapshots")
            .select("url,metrics_json")
            .eq("job_id", job_id)
            .limit(1)
            .execute()
        )
        if not row.data:
            return {}
        return {"url": row.data[0].get("url", ""), "metrics": row.data[0].get("metrics_json", {})}

    async def _fetch_gsc(self, client: httpx.AsyncClient, site_url: str) -> dict[str, Any]:
        encoded = site_url.rstrip("/").replace("://", "%3A//")
        url = GSC_SEARCH_ANALYTICS.format(site=encoded)
        headers = {"Authorization": f"Bearer {self._access_token}"}
        payload = {"startDate": "2026-01-01", "endDate": "2026-12-31", "dimensions": ["page"], "rowLimit": 10}
        resp = await client.post(url, json=payload, headers=headers)
        if resp.status_code != 200:
            return {"impressions": 0, "clicks": 0, "position": 0.0}
        rows = resp.json().get("rows", [])
        if not rows:
            return {"impressions": 0, "clicks": 0, "position": 0.0}
        first = rows[0]
        return {
            "impressions": first.get("impressions", 0),
            "clicks": first.get("clicks", 0),
            "position": first.get("position", 0.0),
        }

    async def _fetch_rank(self, client: httpx.AsyncClient, site_url: str) -> int:
        keyword = site_url.split("//")[-1].rstrip("/")
        payload = [{"keyword": keyword, "location_code": 2840, "language_code": "en", "depth": 10}]
        resp = await client.post(DATAFORSEO_SERP_URL, json=payload, auth=(self._dfs_login, self._dfs_password))
        if resp.status_code != 200:
            return 0
        for task in resp.json().get("tasks", []):
            for result in task.get("result", []):
                items = result.get("items", [])
                if items:
                    return items[0].get("rank_absolute", 0)
        return 0

    async def _fetch_backlinks(self, client: httpx.AsyncClient, site_url: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self._ahrefs_key}", "Accept": "application/json"}
        params = {"target": site_url, "mode": "exact", "limit": "100"}
        resp = await client.get(AHREFS_BACKLINKS_URL, headers=headers, params=params)
        if resp.status_code != 200:
            return {"count": 0, "referring_domains": 0}
        data = resp.json()
        backlinks = data.get("backlinks", []) if isinstance(data, dict) else []
        domains = {b.get("referring_domain") for b in backlinks if b.get("referring_domain")}
        return {"count": len(backlinks), "referring_domains": len(domains)}

    async def run(self, job_id: str, **_: Any) -> dict[str, Any]:
        log.info("day30_agent.run", job_id=job_id)

        baseline = self._load_baseline(job_id)
        site_url = baseline.get("url", "")
        if not site_url:
            log.warning("day30_agent.no_baseline", job_id=job_id)
            return {}

        async with httpx.AsyncClient(timeout=30) as client:
            gsc = await self._fetch_gsc(client, site_url)
            rank = await self._fetch_rank(client, site_url)
            backlinks = await self._fetch_backlinks(client, site_url)

        bl = baseline.get("metrics", {})
        report = {
            "checkpoint": "day30",
            "current": {**gsc, "rank": rank, "backlinks": backlinks},
            "baseline": bl,
            "delta": {
                "impressions": gsc["impressions"] - bl.get("impressions", 0),
                "clicks": gsc["clicks"] - bl.get("clicks", 0),
                "position": gsc["position"] - bl.get("position", 0.0),
                "rank": rank - bl.get("rank", 0),
            },
        }

        self._db.table("aftercare_reports").upsert(
            {"job_id": job_id, "checkpoint": "day30", "data_json": report}
        ).execute()
        log.info("day30_agent.complete", job_id=job_id, rank=rank, backlinks=backlinks["count"])
        return report

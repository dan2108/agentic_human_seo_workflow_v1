"""MonitorAgent — daily Celery cron scans active jobs for rank/traffic anomalies.

Compares current rank against baseline_snapshots for every job that has a
baseline. Emits to monitor_alerts when:
  - rank drops 10+ positions vs baseline (warning)
  - rank drops 20+ positions vs baseline (critical)

Decay detection (60-day stagnation) is deferred — needs a rank-history
table to compare against; will land in Sprint 6.
"""
from typing import Any
import httpx
import structlog

log = structlog.get_logger()

DATAFORSEO_SERP_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"


class MonitorAgent:
    def __init__(self, db, dataforseo_login, dataforseo_password):
        self._db = db
        self._dfs_login = dataforseo_login
        self._dfs_password = dataforseo_password

    def _load_active_baselines(self):
        row = (
            self._db.table("baseline_snapshots")
            .select("job_id,url,metrics_json")
            .limit(500)
            .execute()
        )
        return row.data or []

    async def _fetch_rank(self, client, site_url):
        keyword = site_url.split("//")[-1].rstrip("/")
        payload = [{"keyword": keyword, "location_code": 2840, "language_code": "en", "depth": 20}]
        resp = await client.post(DATAFORSEO_SERP_URL, json=payload, auth=(self._dfs_login, self._dfs_password))
        if resp.status_code != 200:
            return 0
        for task in resp.json().get("tasks", []):
            for result in task.get("result", []):
                items = result.get("items", [])
                if items:
                    return items[0].get("rank_absolute", 0)
        return 0

    def _emit_alert(self, site_url, alert_type, severity, data):
        self._db.table("monitor_alerts").insert({
            "site_url": site_url,
            "alert_type": alert_type,
            "severity": severity,
            "data_json": data,
        }).execute()

    async def run(self, **_):
        log.info("monitor_agent.run")
        baselines = self._load_active_baselines()
        alerts_emitted = 0

        async with httpx.AsyncClient(timeout=30) as client:
            for baseline in baselines:
                site_url = baseline.get("url", "")
                if not site_url:
                    continue
                metrics = baseline.get("metrics_json", {})
                baseline_rank = metrics.get("rank", 0)
                if not baseline_rank:
                    continue

                current_rank = await self._fetch_rank(client, site_url)
                if not current_rank:
                    continue
                rank_drop = current_rank - baseline_rank

                if rank_drop >= 20:
                    self._emit_alert(site_url, "rank_drop", "critical", {
                        "baseline_rank": baseline_rank, "current_rank": current_rank, "drop": rank_drop,
                    })
                    alerts_emitted += 1
                elif rank_drop >= 10:
                    self._emit_alert(site_url, "rank_drop", "warning", {
                        "baseline_rank": baseline_rank, "current_rank": current_rank, "drop": rank_drop,
                    })
                    alerts_emitted += 1

        log.info("monitor_agent.complete", alerts=alerts_emitted, scanned=len(baselines))
        return {"alerts": alerts_emitted, "scanned": len(baselines)}

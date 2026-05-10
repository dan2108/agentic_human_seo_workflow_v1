"""Day 90 aftercare — full performance pull + Claude ROI narrative + outcome classification.

Runs 90 days after publish. Classification is rule-based first (deterministic,
auditable); LLM is used only for ambiguous cases.
"""
import json
from typing import Any
import anthropic
import httpx
import structlog

log = structlog.get_logger()

GSC_SEARCH_ANALYTICS = "https://www.googleapis.com/webmasters/v3/sites/{site}/searchAnalytics/query"
DATAFORSEO_SERP_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
AHREFS_BACKLINKS_URL = "https://api.ahrefs.com/v3/site-explorer/backlinks"

VALID_OUTCOMES = {"winner", "steady", "underperformer", "loser"}


def _classify_outcome(delta: dict, current: dict, baseline: dict) -> tuple[str, bool]:
    rank_delta = delta.get("rank", 0)
    clicks_now = current.get("clicks", 0)
    clicks_base = max(baseline.get("clicks", 0), 1)
    clicks_ratio = clicks_now / clicks_base

    if rank_delta >= 15 or clicks_ratio < 0.1:
        return ("loser", False)
    if rank_delta <= -5 and clicks_ratio >= 2.0:
        return ("winner", False)
    if rank_delta >= 5 or clicks_ratio < 0.5:
        return ("underperformer", False)
    if abs(rank_delta) <= 3 and 0.5 <= clicks_ratio <= 2.0:
        return ("steady", False)
    return ("steady", True)


class Day90Agent:
    def __init__(self, db, access_token, dataforseo_login, dataforseo_password, ahrefs_api_key, anthropic_api_key):
        self._db = db
        self._access_token = access_token
        self._dfs_login = dataforseo_login
        self._dfs_password = dataforseo_password
        self._ahrefs_key = ahrefs_api_key
        self._anthropic = anthropic.Anthropic(api_key=anthropic_api_key)

    def _load_baseline(self, job_id):
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

    async def _fetch_gsc(self, client, site_url):
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

    async def _fetch_rank(self, client, site_url):
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

    async def _fetch_backlinks(self, client, site_url):
        headers = {"Authorization": f"Bearer {self._ahrefs_key}", "Accept": "application/json"}
        params = {"target": site_url, "mode": "exact", "limit": "100"}
        resp = await client.get(AHREFS_BACKLINKS_URL, headers=headers, params=params)
        if resp.status_code != 200:
            return {"count": 0, "referring_domains": 0}
        data = resp.json()
        backlinks = data.get("backlinks", []) if isinstance(data, dict) else []
        domains = {b.get("referring_domain") for b in backlinks if b.get("referring_domain")}
        return {"count": len(backlinks), "referring_domains": len(domains)}

    def _llm_classify(self, report):
        prompt = (
            "Classify this content 90-day performance as exactly one of: "
            "winner, steady, underperformer, loser. "
            "Return JSON with key outcome only.\n\n"
            f"Metrics: {json.dumps(report)}"
        )
        try:
            msg = self._anthropic.messages.create(
                model="claude-haiku-4-5",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            parsed = json.loads(msg.content[0].text)
            outcome = parsed.get("outcome", "steady")
            return outcome if outcome in VALID_OUTCOMES else "steady"
        except Exception as exc:
            log.warning("day90.llm_classify_failed", error=str(exc))
            return "steady"

    def _generate_narrative(self, report, outcome):
        prompt = (
            f"Write a 2-paragraph ROI narrative for SEO content classified as {outcome}. "
            "First paragraph: what happened, with specific numbers. "
            "Second paragraph: recommended next action.\n\n"
            f"Metrics: {json.dumps(report)}"
        )
        try:
            msg = self._anthropic.messages.create(
                model="claude-haiku-4-5",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text
        except Exception as exc:
            log.warning("day90.narrative_failed", error=str(exc))
            return ""

    async def run(self, job_id, **_):
        log.info("day90_agent.run", job_id=job_id)

        baseline = self._load_baseline(job_id)
        site_url = baseline.get("url", "")
        if not site_url:
            log.warning("day90_agent.no_baseline", job_id=job_id)
            return {}

        async with httpx.AsyncClient(timeout=30) as client:
            gsc = await self._fetch_gsc(client, site_url)
            rank = await self._fetch_rank(client, site_url)
            backlinks = await self._fetch_backlinks(client, site_url)

        bl = baseline.get("metrics", {})
        current = {**gsc, "rank": rank, "backlinks": backlinks}
        delta = {
            "impressions": gsc["impressions"] - bl.get("impressions", 0),
            "clicks": gsc["clicks"] - bl.get("clicks", 0),
            "position": gsc["position"] - bl.get("position", 0.0),
            "rank": rank - bl.get("rank", 0),
        }

        outcome, ambiguous = _classify_outcome(delta, current, bl)
        if ambiguous:
            outcome = self._llm_classify({"current": current, "baseline": bl, "delta": delta})

        narrative = self._generate_narrative({"current": current, "baseline": bl, "delta": delta}, outcome)

        report = {
            "checkpoint": "day90",
            "current": current,
            "baseline": bl,
            "delta": delta,
            "outcome": outcome,
            "narrative": narrative,
        }

        self._db.table("aftercare_reports").upsert(
            {"job_id": job_id, "checkpoint": "day90", "data_json": report}
        ).execute()
        self._db.table("content_outcomes").upsert(
            {"job_id": job_id, "outcome": outcome}
        ).execute()

        log.info("day90_agent.complete", job_id=job_id, outcome=outcome)
        return report

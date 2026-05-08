from typing import Any
import httpx
import structlog
from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class TechnicalAgent(BaseAuditAgent):
    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("technical_agent.run", job_id=job_id)
        checks: dict[str, Any] = {}

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(site_url)
            ttfb = resp.elapsed.total_seconds() * 1000

            robots_resp = await client.get(site_url.rstrip("/") + "/robots.txt")
            sitemap_resp = await client.get(site_url.rstrip("/") + "/sitemap.xml")

        checks = {
            "ttfb_ms": round(ttfb, 2),
            "status_code": resp.status_code,
            "has_robots_txt": robots_resp.status_code == 200,
            "has_sitemap_xml": sitemap_resp.status_code in (200, 301),
            "is_https": site_url.startswith("https"),
            "redirects_to_https": str(resp.url).startswith("https"),
        }
        return self._persist(job_id, "technical", checks)

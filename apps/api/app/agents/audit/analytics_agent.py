import re
from typing import Any
import httpx
from bs4 import BeautifulSoup
import structlog
from app.agents.base import BaseAuditAgent

log = structlog.get_logger()

GA4_PATTERN = re.compile(r"G-[A-Z0-9]+")
GTM_PATTERN = re.compile(r"GTM-[A-Z0-9]+")


class AnalyticsAgent(BaseAuditAgent):
    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("analytics_agent.run", job_id=job_id)

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(site_url)

        html = resp.text
        ga4_match = GA4_PATTERN.search(html)
        gtm_match = GTM_PATTERN.search(html)

        soup = BeautifulSoup(html, "html.parser")
        has_gtag = any("gtag" in str(s) for s in soup.find_all("script"))

        data = {
            "has_ga4": ga4_match is not None,
            "measurement_id": ga4_match.group() if ga4_match else None,
            "has_gtm": gtm_match is not None,
            "gtm_id": gtm_match.group() if gtm_match else None,
            "has_gtag_js": has_gtag,
        }
        return self._persist(job_id, "analytics", data)

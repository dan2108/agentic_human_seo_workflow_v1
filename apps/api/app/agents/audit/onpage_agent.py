import re
from typing import Any
import httpx
from bs4 import BeautifulSoup
import structlog
from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class OnPageAgent(BaseAuditAgent):
    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("onpage_agent.run", job_id=job_id)

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(site_url)

        soup = BeautifulSoup(resp.text, "html.parser")

        title_tag = soup.find("title")
        desc_tag = soup.find("meta", attrs={"name": "description"})
        h1 = soup.find("h1")
        headings = {
            f"h{level}": [h.get_text(strip=True) for h in soup.find_all(f"h{level}")]
            for level in range(1, 7)
        }
        schema_tags = [s.get("type", "") for s in soup.find_all("script", type="application/ld+json")]
        word_count = len(re.findall(r"\w+", soup.get_text()))

        data = {
            "title": title_tag.get_text(strip=True) if title_tag else None,
            "title_length": len(title_tag.get_text(strip=True)) if title_tag else 0,
            "meta_description": desc_tag["content"] if desc_tag else None,
            "h1": h1.get_text(strip=True) if h1 else None,
            "headings": headings,
            "schema_types": schema_tags,
            "word_count": word_count,
        }
        return self._persist(job_id, "onpage", data)

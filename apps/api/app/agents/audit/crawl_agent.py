import re
from typing import Any
import httpx
from bs4 import BeautifulSoup
import structlog
from app.agents.base import BaseAuditAgent

log = structlog.get_logger()


class CrawlAgent(BaseAuditAgent):
    async def run(self, job_id: str, site_url: str) -> dict[str, Any]:
        log.info("crawl_agent.run", job_id=job_id, site_url=site_url)
        pages: list[dict] = []

        async with httpx.AsyncClient(follow_redirects=True, timeout=30) as client:
            resp = await client.get(site_url)
            soup = BeautifulSoup(resp.text, "html.parser")

            title = soup.find("title")
            h1 = soup.find("h1")
            canonical_tag = soup.find("link", rel="canonical")
            word_count = len(re.findall(r"\w+", soup.get_text()))

            pages.append({
                "url": str(resp.url),
                "status_code": resp.status_code,
                "title": title.get_text(strip=True) if title else None,
                "h1": h1.get_text(strip=True) if h1 else None,
                "canonical": canonical_tag["href"] if canonical_tag else None,
                "word_count": word_count,
            })

        data = {"pages": pages, "pages_crawled": len(pages)}
        return self._persist(job_id, "crawl", data)
